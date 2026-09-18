from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Float, Index
from sqlalchemy.orm import relationship

from app.database.session import Base
from app.models.user import gen_uuid


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, default=gen_uuid)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    title = Column(String, nullable=False)
    description_raw = Column(Text, nullable=False)

    # Parsed JD fields (stored as JSON-encoded text for SQLite portability)
    required_skills = Column(Text, default="[]")   # JSON list[str]
    preferred_skills = Column(Text, default="[]")  # JSON list[str]
    required_experience_years = Column(Float, default=0)
    education_requirement = Column(String, nullable=True)
    keywords = Column(Text, default="[]")           # JSON list[str]
    responsibilities = Column(Text, default="[]")   # JSON list[str]

    # Configurable scoring weights (JSON-encoded dict), falls back to global defaults if null
    scoring_weights = Column(Text, nullable=True)

    status = Column(String, default="active")  # active | closed | draft

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                         onupdate=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="jobs")
    analyses = relationship("ResumeAnalysis", back_populates="job", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_jobs_owner_status", "owner_id", "status"),
    )
