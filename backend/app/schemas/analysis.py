from datetime import datetime

from pydantic import BaseModel

from app.schemas.resume import CandidateOut


class AnalysisOut(BaseModel):
    id: str
    resume_id: str
    job_id: str
    overall_score: float
    skills_score: float
    experience_score: float
    semantic_score: float
    education_score: float
    keyword_score: float
    matching_skills: list[str]
    missing_skills: list[str]
    strengths: list[str]
    gaps: list[str]
    ai_summary: str | None
    recommendation: str
    analyzed_at: datetime

    class Config:
        from_attributes = True


class RankedCandidateOut(BaseModel):
    resume_id: str
    analysis: AnalysisOut
    candidate: CandidateOut | None
    original_filename: str


class ComparisonRequest(BaseModel):
    resume_ids: list[str]


class AnalyticsOut(BaseModel):
    total_candidates: int
    processed_resumes: int
    failed_resumes: int
    shortlisted_candidates: int  # Strong + Good match
    average_match_score: float
    score_distribution: dict[str, int]  # bucket label -> count
    recommendation_breakdown: dict[str, int]
    top_skills: list[dict]  # [{"skill": str, "count": int}]
