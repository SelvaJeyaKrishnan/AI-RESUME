from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Float, Index
from sqlalchemy.orm import relationship

from app.database.session import Base
from app.models.user import gen_uuid


class ResumeAnalysis(Base):
    """The result of matching one resume against one job."""
    __tablename__ = "resume_analyses"

    id = Column(String, primary_key=True, default=gen_uuid)
    resume_id = Column(String, ForeignKey("resumes.id"), nullable=False, index=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False, index=True)

    overall_score = Column(Float, nullable=False)  # 0-100
    skills_score = Column(Float, nullable=False)
    experience_score = Column(Float, nullable=False)
    semantic_score = Column(Float, nullable=False)
    education_score = Column(Float, nullable=False)
    keyword_score = Column(Float, nullable=False)

    matching_skills = Column(Text, default="[]")   # JSON list[str]
    missing_skills = Column(Text, default="[]")    # JSON list[str]

    strengths = Column(Text, default="[]")         # JSON list[str]
    gaps = Column(Text, default="[]")               # JSON list[str]
    ai_summary = Column(Text, nullable=True)

    recommendation = Column(String, nullable=False)  # Strong Match | Good Match | Potential Match | Low Match

    analyzed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    resume = relationship("Resume", back_populates="analyses")
    job = relationship("Job", back_populates="analyses")

    __table_args__ = (
        Index("ix_analysis_resume_job", "resume_id", "job_id", unique=True),
    )
