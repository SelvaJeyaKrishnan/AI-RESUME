"""
Transparent ATS (Applicant Tracking System) compatibility scoring.

Every factor here is computed from the actual resume text, the parsed
resume entities, and the parsed target job description. Nothing is
hardcoded or randomised. Each factor returns a score, the evidence that
produced it, and a concrete suggestion, so the UI can explain exactly
why a resume scored the way it did.
"""
import re
from dataclasses import dataclass, field

from app.ml.jd_parser import ParsedJob
from app.ml.resume_parser import ParsedCandidate

# Section headers an ATS parser expects to find
EXPECTED_SECTIONS = {
    "experience": r"(work experience|professional experience|experience|employment)",
    "education": r"(education|academic|qualifications)",
    "skills": r"(skills|technical skills|core competencies)",
}

# Characters/patterns that commonly break ATS text extraction
PROBLEM_GLYPHS = re.compile(r"[\u2502\u2500\u2591\u2592\u2593\u25a0-\u25ff\uf000-\uf8ff]")
BULLET_RE = re.compile(r"^\s*[\u2022\u25cf\u25aa\-\*\u2013]\s+", re.MULTILINE)
QUANTIFIED_RE = re.compile(r"\b\d+(?:\.\d+)?\s*(%|percent|x|k\b|million|users|customers|hours|days|weeks)|\b\d{2,}\b", re.IGNORECASE)
WEAK_VERBS = ["responsible for", "worked on", "helped with", "involved in", "duties included", "assisted with"]
STRONG_VERBS = ["built", "designed", "led", "shipped", "reduced", "increased", "automated", "architected",
                 "implemented", "launched", "optimized", "delivered", "migrated", "scaled", "owned"]


@dataclass
class ATSFactor:
    key: str
    label: str
    score: float           # 0-100
    weight: float          # contribution to the overall ATS score
    detail: str            # what we actually found
    suggestion: str        # what to do about it


@dataclass
class ATSResult:
    overall: float
    factors: list[ATSFactor] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "overall": self.overall,
            "factors": [
                {
                    "key": f.key, "label": f.label, "score": f.score,
                    "weight": f.weight, "detail": f.detail, "suggestion": f.suggestion,
                }
                for f in self.factors
            ],
        }


def _score_keyword_relevance(resume_text: str, job: ParsedJob) -> ATSFactor:
    keywords = job.keywords or []
    if not keywords:
        return ATSFactor("keywords", "Keyword relevance", 60.0, 0.20,
                         "No distinctive keywords could be extracted from the target job description.",
                         "Paste a fuller job description so keyword matching can be measured properly.")
    low = resume_text.lower()
    hits = [k for k in keywords if k in low]
    score = round(len(hits) / len(keywords) * 100, 1)
    missing = [k for k in keywords if k not in low][:6]
    return ATSFactor(
        "keywords", "Keyword relevance", score, 0.20,
        f"Your resume contains {len(hits)} of {len(keywords)} keywords found in the job description.",
        (f"Consider naturally working in terms like: {', '.join(missing)}." if missing
         else "Your keyword coverage against this job description is strong."),
    )


def _score_structure(resume_text: str, candidate: ParsedCandidate) -> ATSFactor:
    found, missing = [], []
    for name, pattern in EXPECTED_SECTIONS.items():
        if re.search(rf"(?im)^\s*{pattern}\s*:?\s*$", resume_text) or re.search(rf"(?i){pattern}", resume_text):
            found.append(name)
        else:
            missing.append(name)

    contact_bits = sum(bool(x) for x in (candidate.email, candidate.phone))
    section_score = len(found) / len(EXPECTED_SECTIONS) * 70
    contact_score = contact_bits / 2 * 30
    score = round(section_score + contact_score, 1)

    detail_parts = [f"Detected sections: {', '.join(found) if found else 'none'}."]
    if not candidate.email:
        detail_parts.append("No email address could be parsed.")
    if not candidate.phone:
        detail_parts.append("No phone number could be parsed.")

    suggestion = "Your resume has a clear, parseable structure."
    if missing or contact_bits < 2:
        needed = missing + ([] if candidate.email else ["a parseable email"]) + ([] if candidate.phone else ["a phone number"])
        suggestion = f"Add clearly labelled headings / details for: {', '.join(needed)}."

    return ATSFactor("structure", "Resume structure", score, 0.20, " ".join(detail_parts), suggestion)


def _score_skills_alignment(candidate_skills: set[str], job: ParsedJob) -> ATSFactor:
    required = set(job.required_skills)
    preferred = set(job.preferred_skills)
    if not required and not preferred:
        return ATSFactor("skills", "Skills alignment", 60.0, 0.25,
                         "No specific skills could be detected in the target job description.",
                         "Add a more detailed job description listing required technologies.")
    matched_req = required & candidate_skills
    matched_pref = preferred & candidate_skills
    req_ratio = len(matched_req) / len(required) if required else 1.0
    pref_ratio = len(matched_pref) / len(preferred) if preferred else 0.0
    score = round((req_ratio * 0.8 + pref_ratio * 0.2) * 100 if preferred else req_ratio * 100, 1)
    missing = sorted(required - candidate_skills)[:6]
    return ATSFactor(
        "skills", "Skills alignment", score, 0.25,
        f"You match {len(matched_req)} of {len(required)} required skills"
        + (f" and {len(matched_pref)} of {len(preferred)} preferred skills." if preferred else "."),
        (f"The job asks for these you don't appear to list: {', '.join(missing)}." if missing
         else "You cover the required skills this job lists."),
    )


def _score_formatting(resume_text: str) -> ATSFactor:
    issues = []
    score = 100.0

    if PROBLEM_GLYPHS.search(resume_text):
        score -= 20
        issues.append("contains box-drawing or icon-font characters that ATS parsers often mangle")

    bullets = len(BULLET_RE.findall(resume_text))
    if bullets == 0:
        score -= 15
        issues.append("uses no bullet points, which makes achievements harder to scan")

    words = len(resume_text.split())
    if words < 150:
        score -= 25
        issues.append(f"is very short ({words} words) — ATS systems may find too little to index")
    elif words > 1200:
        score -= 10
        issues.append(f"is quite long ({words} words) — consider tightening it")

    # Very long unbroken lines often indicate table/column extraction problems
    long_lines = [l for l in resume_text.splitlines() if len(l) > 200]
    if len(long_lines) > 3:
        score -= 15
        issues.append("has several very long unbroken lines, often a sign of multi-column or table layout")

    score = round(max(score, 0), 1)
    detail = ("Your resume " + "; ".join(issues) + ".") if issues else "No common ATS formatting problems detected."
    suggestion = ("Use a single-column layout, standard bullet characters, and plain text headings."
                  if issues else "Formatting looks ATS-friendly — keep the single-column, plain-text structure.")
    return ATSFactor("formatting", "Formatting", score, 0.15, detail, suggestion)


def _score_jd_match(semantic_score: float) -> ATSFactor:
    return ATSFactor(
        "jd_match", "Job description matching", round(semantic_score, 1), 0.10,
        f"Overall textual and semantic similarity to the target job description is {round(semantic_score)}%.",
        ("Mirror more of the job description's own language in your summary and bullets."
         if semantic_score < 60 else "Your resume language lines up well with this job description."),
    )


def _score_experience_relevance(candidate: ParsedCandidate, job: ParsedJob) -> ATSFactor:
    required = job.required_experience_years or 0
    actual = candidate.years_of_experience or 0

    if required <= 0:
        score = 75.0 if actual > 0 else 50.0
        detail = f"The job doesn't state a specific experience requirement; your resume indicates about {actual:g} year(s)."
        suggestion = "Make your total years of relevant experience explicit near the top of the resume."
    else:
        ratio = actual / required if required else 0
        score = round(min(100.0, ratio * 100), 1)
        detail = f"The job asks for about {required:g}+ year(s); your resume indicates about {actual:g} year(s)."
        suggestion = ("Highlight internships, freelance work, and substantial projects to close the experience gap."
                      if ratio < 1 else "Your experience level lines up with what this role asks for.")

    # Job-title overlap gives a secondary signal
    if job.title and candidate.job_titles:
        title_words = {w for w in re.findall(r"[a-z]+", job.title.lower()) if len(w) > 3}
        resume_title_words = {w for t in candidate.job_titles for w in re.findall(r"[a-z]+", t.lower())}
        if title_words & resume_title_words:
            score = min(100.0, score + 10)
            detail += " Your past job titles overlap with the target role."

    return ATSFactor("experience", "Experience relevance", round(score, 1), 0.10, detail, suggestion)


def compute_ats_score(
    resume_text: str,
    candidate: ParsedCandidate,
    candidate_skills: set[str],
    job: ParsedJob,
    semantic_score: float,
) -> ATSResult:
    """Produce a weighted, fully-explained ATS compatibility score."""
    factors = [
        _score_keyword_relevance(resume_text, job),
        _score_structure(resume_text, candidate),
        _score_skills_alignment(candidate_skills, job),
        _score_formatting(resume_text),
        _score_jd_match(semantic_score),
        _score_experience_relevance(candidate, job),
    ]
    overall = round(sum(f.score * f.weight for f in factors), 1)
    return ATSResult(overall=overall, factors=factors)


def detect_content_quality(resume_text: str) -> tuple[float, list[str]]:
    """Secondary content-quality signal used by the overall resume rating.
    Returns (score, list of observations)."""
    observations = []
    score = 70.0
    low = resume_text.lower()

    quantified = len(QUANTIFIED_RE.findall(resume_text))
    if quantified >= 5:
        score += 15
        observations.append(f"Good use of numbers and measurable detail ({quantified} numeric mentions).")
    elif quantified >= 2:
        score += 5
        observations.append("Some measurable detail present, but more would strengthen your bullets.")
    else:
        score -= 15
        observations.append("Very few quantified achievements — numbers make impact concrete.")

    weak_hits = [v for v in WEAK_VERBS if v in low]
    if weak_hits:
        score -= min(15, len(weak_hits) * 5)
        observations.append(f"Uses passive phrasing such as: {', '.join(weak_hits[:3])}.")

    strong_hits = [v for v in STRONG_VERBS if v in low]
    if strong_hits:
        score += min(15, len(strong_hits) * 3)
        observations.append(f"Uses strong action verbs such as: {', '.join(strong_hits[:4])}.")

    has_summary = bool(re.search(r"(?im)^\s*(summary|profile|objective|about me)\s*:?\s*$", resume_text))
    if has_summary:
        score += 5
        observations.append("Includes a professional summary section.")
    else:
        score -= 10
        observations.append("No professional summary section detected.")

    return round(max(0.0, min(100.0, score)), 1), observations
