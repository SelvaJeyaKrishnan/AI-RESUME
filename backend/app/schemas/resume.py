from datetime import datetime

from pydantic import BaseModel


class CandidateOut(BaseModel):
    id: str
    full_name: str | None
    email: str | None
    phone: str | None
    location: str | None
    education: list[dict]
    work_experience: list[dict]
    years_of_experience: float
    projects: list[dict]
    certifications: list[str]
    job_titles: list[str]
    skills: list[str] = []

    class Config:
        from_attributes = True


class ResumeOut(BaseModel):
    id: str
    original_filename: str
    file_type: str
    parse_status: str
    parse_error: str | None
    created_at: datetime
    candidate: CandidateOut | None = None
    raw_text_preview: str | None = None

    class Config:
        from_attributes = True


class ResumeUploadResult(BaseModel):
    resume: ResumeOut
    duplicate: bool = False
