from datetime import datetime

from pydantic import BaseModel, Field


class JobCreate(BaseModel):
    title: str | None = None
    description_raw: str = Field(min_length=20)
    scoring_weights: dict[str, float] | None = None


class JobUpdate(BaseModel):
    title: str | None = None
    description_raw: str | None = None
    status: str | None = None
    scoring_weights: dict[str, float] | None = None


class JobOut(BaseModel):
    id: str
    title: str
    description_raw: str
    required_skills: list[str]
    preferred_skills: list[str]
    required_experience_years: float
    education_requirement: str | None
    keywords: list[str]
    responsibilities: list[str]
    status: str
    created_at: datetime
    candidate_count: int = 0
    avg_score: float | None = None

    class Config:
        from_attributes = True
