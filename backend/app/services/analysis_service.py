import json

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ml.jd_parser import ParsedJob
from app.ml.matching_engine import compute_match
from app.ml.resume_parser import ParsedCandidate
from app.models.job import Job
from app.models.resume import Resume, Candidate
from app.models.analysis import ResumeAnalysis
from app.utils.json_utils import from_json, to_json


def _job_to_parsed(job: Job) -> ParsedJob:
    return ParsedJob(
        title=job.title,
        required_skills=from_json(job.required_skills, []),
        preferred_skills=from_json(job.preferred_skills, []),
        required_experience_years=job.required_experience_years or 0.0,
        education_requirement=job.education_requirement,
        keywords=from_json(job.keywords, []),
        responsibilities=from_json(job.responsibilities, []),
    )


def _candidate_to_parsed(candidate: Candidate | None) -> ParsedCandidate:
    if candidate is None:
        return ParsedCandidate()
    return ParsedCandidate(
        full_name=candidate.full_name,
        email=candidate.email,
        phone=candidate.phone,
        location=candidate.location,
        education=from_json(candidate.education, []),
        work_experience=from_json(candidate.work_experience, []),
        years_of_experience=candidate.years_of_experience or 0.0,
        projects=from_json(candidate.projects, []),
        certifications=from_json(candidate.certifications, []),
        job_titles=from_json(candidate.job_titles, []),
    )


def run_analysis(db: Session, resume: Resume, job: Job) -> ResumeAnalysis:
    if resume.parse_status != "success" or not resume.raw_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Resume has not been successfully parsed yet and cannot be analyzed.",
        )

    candidate = db.query(Candidate).filter(Candidate.resume_id == resume.id).first()
    parsed_candidate = _candidate_to_parsed(candidate)
    parsed_job = _job_to_parsed(job)

    weights = None
    if job.scoring_weights:
        try:
            weights = json.loads(job.scoring_weights)
        except json.JSONDecodeError:
            weights = None

    result = compute_match(
        candidate=parsed_candidate,
        resume_text=resume.raw_text,
        job=parsed_job,
        job_description_text=job.description_raw,
        weights=weights,
    )

    existing = (
        db.query(ResumeAnalysis)
        .filter(ResumeAnalysis.resume_id == resume.id, ResumeAnalysis.job_id == job.id)
        .first()
    )
    analysis = existing or ResumeAnalysis(resume_id=resume.id, job_id=job.id)

    analysis.overall_score = result.overall_score
    analysis.skills_score = result.skills_score
    analysis.experience_score = result.experience_score
    analysis.semantic_score = result.semantic_score
    analysis.education_score = result.education_score
    analysis.keyword_score = result.keyword_score
    analysis.matching_skills = to_json(result.matching_skills)
    analysis.missing_skills = to_json(result.missing_skills)
    analysis.strengths = to_json(result.strengths)
    analysis.gaps = to_json(result.gaps)
    analysis.ai_summary = result.ai_summary
    analysis.recommendation = result.recommendation

    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis
