from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Float, Integer, Boolean, Index
from sqlalchemy.orm import relationship

from app.database.session import Base
from app.models.user import gen_uuid


class CareerReport(Base):
    """A candidate-facing career report: one resume analyzed against one target
    job description, gated behind a communication assessment."""
    __tablename__ = "career_reports"

    id = Column(String, primary_key=True, default=gen_uuid)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    resume_id = Column(String, ForeignKey("resumes.id"), nullable=False, index=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False, index=True)

    target_job_description = Column(Text, nullable=False)

    # Computed analysis payloads (JSON-encoded)
    ats_payload = Column(Text, default="{}")          # ATSResult.as_dict()
    ratings_payload = Column(Text, default="[]")      # category ratings
    roles_payload = Column(Text, default="[]")        # RoleMatch dicts
    skill_gap_payload = Column(Text, default="{}")    # have / required / missing
    tips_payload = Column(Text, default="[]")         # ImprovementTip dicts
    strengths = Column(Text, default="[]")
    weaknesses = Column(Text, default="[]")

    overall_score = Column(Float, default=0)
    ats_score = Column(Float, default=0)
    job_match_score = Column(Float, default=0)

    # Gating
    status = Column(String, default="awaiting_assessment")  # awaiting_assessment | complete
    unlocked_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    assessment = relationship("Assessment", back_populates="report", uselist=False,
                               cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_career_reports_owner_created", "owner_id", "created_at"),
    )


class Assessment(Base):
    """The communication + grammar assessment attached to a career report."""
    __tablename__ = "assessments"

    id = Column(String, primary_key=True, default=gen_uuid)
    report_id = Column(String, ForeignKey("career_reports.id"), nullable=False, unique=True)

    questions_payload = Column(Text, nullable=False)  # full questions incl. answers (server-side only)
    answers_payload = Column(Text, default="{}")      # {question_id: selected_option_id}

    total_questions = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    accuracy = Column(Float, default=0)
    band = Column(String, nullable=True)
    band_message = Column(Text, nullable=True)

    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    report = relationship("CareerReport", back_populates="assessment")
