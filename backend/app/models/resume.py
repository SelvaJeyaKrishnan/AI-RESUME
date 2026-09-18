from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Float, Integer, Index
from sqlalchemy.orm import relationship

from app.database.session import Base
from app.models.user import gen_uuid


class Resume(Base):
    """A single uploaded resume file, and the parsed candidate data extracted from it."""
    __tablename__ = "resumes"

    id = Column(String, primary_key=True, default=gen_uuid)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    original_filename = Column(String, nullable=False)
    stored_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # pdf | docx | txt
    file_hash = Column(String, nullable=True, index=True)  # used for duplicate detection
    raw_text = Column(Text, nullable=True)

    parse_status = Column(String, default="pending")  # pending | success | failed
    parse_error = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    candidate = relationship("Candidate", back_populates="resume", uselist=False,
                              cascade="all, delete-orphan")
    analyses = relationship("ResumeAnalysis", back_populates="resume", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_resumes_owner_hash", "owner_id", "file_hash"),
    )


class Candidate(Base):
    """Structured candidate info extracted from a resume."""
    __tablename__ = "candidates"

    id = Column(String, primary_key=True, default=gen_uuid)
    resume_id = Column(String, ForeignKey("resumes.id"), nullable=False, unique=True)

    full_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    location = Column(String, nullable=True)

    education = Column(Text, default="[]")        # JSON list[dict]
    work_experience = Column(Text, default="[]")  # JSON list[dict]
    years_of_experience = Column(Float, default=0)
    projects = Column(Text, default="[]")         # JSON list[dict]
    certifications = Column(Text, default="[]")   # JSON list[str]
    job_titles = Column(Text, default="[]")       # JSON list[str]

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    resume = relationship("Resume", back_populates="candidate")
    skills = relationship("CandidateSkill", back_populates="candidate", cascade="all, delete-orphan")


class Skill(Base):
    """A normalized master skill (dedup'd across candidates/jobs)."""
    __tablename__ = "skills"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, unique=True, nullable=False, index=True)
    category = Column(String, nullable=True)  # e.g. "programming", "cloud", "soft-skill"

    candidate_links = relationship("CandidateSkill", back_populates="skill")


class CandidateSkill(Base):
    """Many-to-many join between Candidate and Skill, with an optional proficiency signal."""
    __tablename__ = "candidate_skills"

    id = Column(String, primary_key=True, default=gen_uuid)
    candidate_id = Column(String, ForeignKey("candidates.id"), nullable=False, index=True)
    skill_id = Column(String, ForeignKey("skills.id"), nullable=False, index=True)
    mentions = Column(Integer, default=1)  # how many times skill appears in resume text

    candidate = relationship("Candidate", back_populates="skills")
    skill = relationship("Skill", back_populates="candidate_links")

    __table_args__ = (
        Index("ix_candidate_skill_unique", "candidate_id", "skill_id", unique=True),
    )
