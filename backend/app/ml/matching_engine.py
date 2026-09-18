"""
The core scoring engine: compares a parsed resume against a parsed job
description across five dimensions and produces a weighted overall score,
plus an explainable breakdown (matching/missing skills, strengths, gaps,
and a plain-language summary).

Semantic similarity uses sentence-transformers when available/enabled; it
falls back to pure TF-IDF cosine similarity (scikit-learn) if the model
can't be loaded (e.g. no internet access to download weights), so the
system degrades gracefully rather than failing.
"""
from dataclasses import dataclass, field
from functools import lru_cache

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.config import get_settings
from app.ml.jd_parser import ParsedJob
from app.ml.resume_parser import ParsedCandidate
from app.ml.skill_extractor import extract_skills

settings = get_settings()

RECOMMENDATION_THRESHOLDS = [
    (85, "Strong Match"),
    (70, "Good Match"),
    (50, "Potential Match"),
    (0, "Low Match"),
]


@dataclass
class MatchResult:
    overall_score: float
    skills_score: float
    experience_score: float
    semantic_score: float
    education_score: float
    keyword_score: float
    matching_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    ai_summary: str = ""
    recommendation: str = "Low Match"


@lru_cache(maxsize=1)
def _get_semantic_model():
    """Lazily load the sentence-transformers model once per process.
    Returns None if disabled or unavailable, so callers can fall back to TF-IDF."""
    if not settings.USE_SEMANTIC_MODEL:
        return None
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer(settings.SEMANTIC_MODEL_NAME)
    except Exception:
        return None


def _tfidf_similarity(text_a: str, text_b: str) -> float:
    if not text_a.strip() or not text_b.strip():
        return 0.0
    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
    try:
        matrix = vectorizer.fit_transform([text_a, text_b])
    except ValueError:
        return 0.0
    sim = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
    return float(np.clip(sim, 0, 1))


def _semantic_similarity(text_a: str, text_b: str) -> float:
    model = _get_semantic_model()
    if model is None:
        return _tfidf_similarity(text_a, text_b)
    try:
        embeddings = model.encode([text_a[:5000], text_b[:5000]], normalize_embeddings=True)
        sim = float(np.dot(embeddings[0], embeddings[1]))
        return float(np.clip(sim, 0, 1))
    except Exception:
        return _tfidf_similarity(text_a, text_b)


def _score_skills(candidate_skills: set[str], required: list[str], preferred: list[str]) -> tuple[float, list[str], list[str]]:
    required_set = set(required)
    preferred_set = set(preferred)
    all_relevant = required_set | preferred_set

    matching = sorted(all_relevant & candidate_skills)
    missing = sorted(required_set - candidate_skills)  # only required skills count as "missing"

    if not all_relevant:
        return 50.0, matching, missing  # neutral score if JD has no detected skills

    # weight required skills more heavily than preferred ones
    required_hit = len(required_set & candidate_skills)
    preferred_hit = len(preferred_set & candidate_skills)
    required_total = max(len(required_set), 1)
    preferred_total = max(len(preferred_set), 1) if preferred_set else 0

    required_ratio = required_hit / required_total
    if preferred_set:
        preferred_ratio = preferred_hit / preferred_total
        score = (required_ratio * 0.8 + preferred_ratio * 0.2) * 100
    else:
        score = required_ratio * 100

    return round(score, 1), matching, missing


def _score_experience(candidate_years: float, required_years: float) -> float:
    if required_years <= 0:
        return 100.0 if candidate_years > 0 else 60.0
    ratio = candidate_years / required_years
    if ratio >= 1:
        # small bonus for meeting/exceeding, capped at 100
        return round(min(100.0, 90 + min(ratio - 1, 1) * 10), 1)
    return round(max(0.0, ratio * 90), 1)  # under-qualified scales down, never hits 100


def _score_education(candidate_education: list[dict], requirement: str | None) -> float:
    if not requirement:
        return 100.0 if candidate_education else 70.0
    if not candidate_education:
        return 30.0
    req_low = requirement.lower()
    for edu in candidate_education:
        line_low = edu.get("degree_line", "").lower()
        if req_low[:4] in line_low:
            return 100.0
    # candidate has *some* education listed, just not an exact match to requirement
    return 55.0


def _score_keywords(resume_text: str, keywords: list[str]) -> float:
    if not keywords:
        return 50.0
    text_low = resume_text.lower()
    hits = sum(1 for kw in keywords if kw in text_low)
    return round((hits / len(keywords)) * 100, 1)


def _recommendation_for(score: float) -> str:
    for threshold, label in RECOMMENDATION_THRESHOLDS:
        if score >= threshold:
            return label
    return "Low Match"


def _build_summary(candidate_name: str | None, score: float, matching: list[str],
                    missing: list[str], exp_score: float) -> str:
    name = candidate_name or "This candidate"
    tier = _recommendation_for(score).lower()
    top_matches = ", ".join(matching[:4]) if matching else "some relevant background"
    if missing:
        gap_text = f"but lacks the {', '.join(missing[:3])} requirement(s) from the job description"
    else:
        gap_text = "and covers the required skill set well"

    exp_note = ""
    if exp_score < 60:
        exp_note = " Experience level is somewhat below what the role calls for."
    elif exp_score >= 90:
        exp_note = " Experience level comfortably meets the role's requirements."

    return (
        f"{name} is a {tier} for this role, showing strength in {top_matches}, "
        f"{gap_text}.{exp_note}"
    ).strip()


def compute_match(
    candidate: ParsedCandidate,
    resume_text: str,
    job: ParsedJob,
    job_description_text: str,
    weights: dict[str, float] | None = None,
) -> MatchResult:
    w = weights or {
        "skills": settings.WEIGHT_SKILLS,
        "experience": settings.WEIGHT_EXPERIENCE,
        "semantic": settings.WEIGHT_SEMANTIC,
        "education": settings.WEIGHT_EDUCATION,
        "keywords": settings.WEIGHT_KEYWORDS,
    }

    candidate_skill_hits = extract_skills(resume_text)
    candidate_skills = set(candidate_skill_hits.keys())

    skills_score, matching_skills, missing_skills = _score_skills(
        candidate_skills, job.required_skills, job.preferred_skills
    )
    experience_score = _score_experience(candidate.years_of_experience, job.required_experience_years)
    semantic_score = round(_semantic_similarity(resume_text, job_description_text) * 100, 1)
    education_score = _score_education(candidate.education, job.education_requirement)
    keyword_score = _score_keywords(resume_text, job.keywords)

    overall = (
        skills_score * w["skills"]
        + experience_score * w["experience"]
        + semantic_score * w["semantic"]
        + education_score * w["education"]
        + keyword_score * w["keywords"]
    )
    overall = round(float(np.clip(overall, 0, 100)), 1)

    strengths = [f"{s}" for s in matching_skills[:6]]
    if experience_score >= 85:
        strengths.append(f"{candidate.years_of_experience:g}+ years of relevant experience")
    if education_score >= 90:
        strengths.append("Meets education requirements")

    gaps = [f"Missing skill: {s}" for s in missing_skills[:6]]
    if experience_score < 60:
        gaps.append("Experience below the role's requirement")
    if education_score < 60:
        gaps.append("Education requirement not clearly met")

    recommendation = _recommendation_for(overall)
    summary = _build_summary(candidate.full_name, overall, matching_skills, missing_skills, experience_score)

    return MatchResult(
        overall_score=overall,
        skills_score=skills_score,
        experience_score=experience_score,
        semantic_score=semantic_score,
        education_score=education_score,
        keyword_score=keyword_score,
        matching_skills=matching_skills,
        missing_skills=missing_skills,
        strengths=strengths,
        gaps=gaps,
        ai_summary=summary,
        recommendation=recommendation,
    )
