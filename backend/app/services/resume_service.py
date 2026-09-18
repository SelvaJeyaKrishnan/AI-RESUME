from sqlalchemy.orm import Session

from app.ml.resume_parser import parse_resume
from app.ml.skill_extractor import extract_skills
from app.models.resume import Resume, Candidate
from app.services.skill_service import sync_candidate_skills
from app.services.text_extraction import extract_text, ExtractionError
from app.utils.json_utils import to_json


def process_resume(db: Session, resume: Resume, contents: bytes) -> Resume:
    """Extract text + structured candidate data from an uploaded resume file,
    persist it, and never raise: failures are recorded on the Resume row so
    one bad file never crashes a batch upload."""
    ext = "." + resume.file_type
    try:
        text = extract_text(contents, ext)
    except ExtractionError as exc:
        resume.parse_status = "failed"
        resume.parse_error = str(exc)
        db.add(resume)
        db.commit()
        db.refresh(resume)
        return resume

    resume.raw_text = text
    resume.parse_status = "success"
    resume.parse_error = None
    db.add(resume)
    db.commit()
    db.refresh(resume)

    parsed = parse_resume(text)

    candidate = db.query(Candidate).filter(Candidate.resume_id == resume.id).first()
    if not candidate:
        candidate = Candidate(resume_id=resume.id)

    candidate.full_name = parsed.full_name
    candidate.email = parsed.email
    candidate.phone = parsed.phone
    candidate.location = parsed.location
    candidate.education = to_json(parsed.education)
    candidate.work_experience = to_json(parsed.work_experience)
    candidate.years_of_experience = parsed.years_of_experience
    candidate.projects = to_json(parsed.projects)
    candidate.certifications = to_json(parsed.certifications)
    candidate.job_titles = to_json(parsed.job_titles)

    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    skill_hits = extract_skills(text)
    sync_candidate_skills(db, candidate.id, skill_hits)

    db.refresh(resume)
    return resume
