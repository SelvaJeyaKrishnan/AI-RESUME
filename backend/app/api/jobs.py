import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.job import Job
from app.models.analysis import ResumeAnalysis
from app.models.user import User
from app.schemas.job import JobCreate, JobUpdate, JobOut
from app.services.job_service import populate_job_from_description
from app.utils.json_utils import from_json

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _to_job_out(db: Session, job: Job) -> JobOut:
    analyses = db.query(ResumeAnalysis).filter(ResumeAnalysis.job_id == job.id).all()
    avg_score = round(sum(a.overall_score for a in analyses) / len(analyses), 1) if analyses else None
    return JobOut(
        id=job.id,
        title=job.title,
        description_raw=job.description_raw,
        required_skills=from_json(job.required_skills, []),
        preferred_skills=from_json(job.preferred_skills, []),
        required_experience_years=job.required_experience_years or 0,
        education_requirement=job.education_requirement,
        keywords=from_json(job.keywords, []),
        responsibilities=from_json(job.responsibilities, []),
        status=job.status,
        created_at=job.created_at,
        candidate_count=len(analyses),
        avg_score=avg_score,
    )


def _get_owned_job(db: Session, job_id: str, user: User) -> Job:
    job = db.query(Job).filter(Job.id == job_id, Job.owner_id == user.id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job


@router.post("", response_model=JobOut, status_code=status.HTTP_201_CREATED)
def create_job(payload: JobCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    job = Job(
        owner_id=user.id,
        title=payload.title or "",
        description_raw=payload.description_raw,
        scoring_weights=json.dumps(payload.scoring_weights) if payload.scoring_weights else None,
    )
    job = populate_job_from_description(job)
    db.add(job)
    db.commit()
    db.refresh(job)
    return _to_job_out(db, job)


@router.get("", response_model=list[JobOut])
def list_jobs(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    jobs = db.query(Job).filter(Job.owner_id == user.id).order_by(Job.created_at.desc()).all()
    return [_to_job_out(db, j) for j in jobs]


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    job = _get_owned_job(db, job_id, user)
    return _to_job_out(db, job)


@router.put("/{job_id}", response_model=JobOut)
def update_job(job_id: str, payload: JobUpdate, db: Session = Depends(get_db),
                user: User = Depends(get_current_user)):
    job = _get_owned_job(db, job_id, user)

    if payload.title is not None:
        job.title = payload.title
    if payload.status is not None:
        job.status = payload.status
    if payload.scoring_weights is not None:
        job.scoring_weights = json.dumps(payload.scoring_weights)
    if payload.description_raw is not None:
        job.description_raw = payload.description_raw
        job = populate_job_from_description(job)

    db.add(job)
    db.commit()
    db.refresh(job)
    return _to_job_out(db, job)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    job = _get_owned_job(db, job_id, user)
    db.delete(job)
    db.commit()
    return None
