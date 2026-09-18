"""
Extracts structured requirements from a raw job description:
required/preferred skills, required experience, education requirement,
job title, keywords, and responsibilities.
"""
import re
from dataclasses import dataclass, field

from app.ml.skill_extractor import extract_skills

PREFERRED_MARKERS = re.compile(
    r"(preferred|nice to have|bonus|good to have|plus)", re.IGNORECASE
)

DEGREE_RE = re.compile(
    r"(bachelor'?s?|master'?s?|phd|ph\.d|doctorate|b\.?tech|m\.?tech|mba|associate'?s? degree)",
    re.IGNORECASE,
)

EXPERIENCE_RE = re.compile(
    r"(\d+)\+?\s*(?:to\s*(\d+)\s*)?years?\s+(?:of\s+)?(?:relevant\s+)?experience", re.IGNORECASE
)

RESPONSIBILITY_HEADER_RE = re.compile(
    r"(?im)^\s*(responsibilities|what you.?ll do|key responsibilities|duties)\s*:?\s*$"
)

STOPWORDS = {
    "the", "and", "for", "with", "you", "our", "are", "will", "have", "this",
    "that", "your", "team", "work", "ability", "strong", "including", "role",
    "years", "experience", "skills", "job", "candidate", "who", "can", "must",
}


@dataclass
class ParsedJob:
    title: str | None = None
    required_skills: list[str] = field(default_factory=list)
    preferred_skills: list[str] = field(default_factory=list)
    required_experience_years: float = 0.0
    education_requirement: str | None = None
    keywords: list[str] = field(default_factory=list)
    responsibilities: list[str] = field(default_factory=list)


def parse_job_description(text: str, provided_title: str | None = None) -> ParsedJob:
    job = ParsedJob()
    job.title = provided_title or _guess_title(text)

    required_section, preferred_section = _split_required_preferred(text)
    required_skill_hits = extract_skills(required_section)
    preferred_skill_hits = extract_skills(preferred_section) if preferred_section else {}

    # Any skill in "preferred" shouldn't also count as required
    job.preferred_skills = sorted(preferred_skill_hits.keys())
    job.required_skills = sorted(
        s for s in required_skill_hits.keys() if s not in preferred_skill_hits
    )

    # if nothing was split into a "preferred" section, treat all detected skills as required
    if not job.preferred_skills and not job.required_skills:
        all_hits = extract_skills(text)
        job.required_skills = sorted(all_hits.keys())

    job.required_experience_years = _extract_experience_years(text)
    job.education_requirement = _extract_education_requirement(text)
    job.keywords = _extract_keywords(text)
    job.responsibilities = _extract_responsibilities(text)

    return job


def _guess_title(text: str) -> str | None:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if lines:
        first = lines[0]
        if len(first) < 100:
            return first
    return None


def _split_required_preferred(text: str) -> tuple[str, str]:
    match = PREFERRED_MARKERS.search(text)
    if match:
        return text[: match.start()], text[match.start():]
    return text, ""


def _extract_experience_years(text: str) -> float:
    m = EXPERIENCE_RE.search(text)
    if not m:
        return 0.0
    try:
        return float(m.group(1))
    except (TypeError, ValueError):
        return 0.0


def _extract_education_requirement(text: str) -> str | None:
    m = DEGREE_RE.search(text)
    return m.group(0) if m else None


def _extract_keywords(text: str, top_n: int = 20) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z+.#-]{2,}", text.lower())
    freq: dict[str, int] = {}
    for w in words:
        if w in STOPWORDS or len(w) < 3:
            continue
        freq[w] = freq.get(w, 0) + 1
    ranked = sorted(freq.items(), key=lambda kv: kv[1], reverse=True)
    return [w for w, _ in ranked[:top_n]]


def _extract_responsibilities(text: str) -> list[str]:
    match = RESPONSIBILITY_HEADER_RE.search(text)
    if not match:
        return []
    remainder = text[match.end():]
    # stop at next all-caps-ish header or blank-blank line
    stop_match = re.search(r"\n\s*\n\s*[A-Z][A-Za-z ]{2,40}\n", remainder)
    section = remainder[: stop_match.start()] if stop_match else remainder[:1500]
    lines = [l.strip("•-*\t ") for l in section.splitlines() if l.strip()]
    return [l[:200] for l in lines[:12] if len(l) > 4]
