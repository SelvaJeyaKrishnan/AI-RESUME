from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.resume import Resume, Candidate
from app.models.user import User
from app.schemas.resume import ResumeOut, CandidateOut, ResumeUploadResult
from app.services.resume_service import process_resume
from app.utils.file_handling import validate_file, compute_file_hash, save_upload, delete_file
from app.utils.json_utils import from_json

router = APIRouter(prefix="/resumes", tags=["resumes"])


def _candidate_out(candidate: Candidate | None) -> CandidateOut | None:
    if not candidate:
        return None
    skill_names = [link.skill.name for link in candidate.skills] if candidate.skills else []
    return CandidateOut(
        id=candidate.id,
        full_name=candidate.full_name,
        email=candidate.email,
        phone=candidate.phone,
        location=candidate.location,
        education=from_json(candidate.education, []),
        work_experience=from_json(candidate.work_experience, []),
        years_of_experience=candidate.years_of_experience or 0,
        projects=from_json(candidate.projects, []),
        certifications=from_json(candidate.certifications, []),
        job_titles=from_json(candidate.job_titles, []),
        skills=skill_names,
    )


def _resume_out(resume: Resume) -> ResumeOut:
    return ResumeOut(
        id=resume.id,
        original_filename=resume.original_filename,
        file_type=resume.file_type,
        parse_status=resume.parse_status,
        parse_error=resume.parse_error,
        created_at=resume.created_at,
        candidate=_candidate_out(resume.candidate),
        raw_text_preview=(resume.raw_text[:4000] if resume.raw_text else None),
    )


def _get_owned_resume(db: Session, resume_id: str, user: User) -> Resume:
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.owner_id == user.id).first()
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    return resume


@router.post("/upload", response_model=list[ResumeUploadResult], status_code=status.HTTP_201_CREATED)
async def upload_resumes(
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Upload one or more resumes. Each file is validated, saved, and parsed
    independently -- a failure on one file is recorded on its Resume row and
    does not stop the rest of the batch from processing."""
    results = []
    for file in files:
        try:
            contents = await file.read()
            ext = validate_file(file, contents)
        except HTTPException as exc:
            # Represent validation failures as a failed Resume record instead of aborting the batch
            results.append(ResumeUploadResult(
                resume=ResumeOut(
                    id="", original_filename=file.filename or "unknown",
                    file_type=ext if 'ext' in dir() else "unknown",
                    parse_status="failed", parse_error=exc.detail,
                    created_at=__import__("datetime").datetime.now(), candidate=None,
                ),
                duplicate=False,
            ))
            continue

        file_hash = compute_file_hash(contents)
        duplicate = (
            db.query(Resume)
            .filter(Resume.owner_id == user.id, Resume.file_hash == file_hash)
            .first()
        )

        stored_path = save_upload(contents, ext, user.id)
        resume = Resume(
            owner_id=user.id,
            original_filename=file.filename or "resume",
            stored_path=stored_path,
            file_type=ext.lstrip("."),
            file_hash=file_hash,
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)

        resume = process_resume(db, resume, contents)
        results.append(ResumeUploadResult(resume=_resume_out(resume), duplicate=bool(duplicate)))

    return results


@router.get("", response_model=list[ResumeOut])
def list_resumes(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    resumes = db.query(Resume).filter(Resume.owner_id == user.id).order_by(Resume.created_at.desc()).all()
    return [_resume_out(r) for r in resumes]


@router.get("/{resume_id}", response_model=ResumeOut)
def get_resume(resume_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    resume = _get_owned_resume(db, resume_id, user)
    return _resume_out(resume)


@router.get("/{resume_id}/download")
def download_resume(resume_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    resume = _get_owned_resume(db, resume_id, user)
    if not Path(resume.stored_path).exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File missing on disk")
    return FileResponse(resume.stored_path, filename=resume.original_filename)


@router.post("/{resume_id}/reprocess", response_model=ResumeOut)
def reprocess_resume(resume_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    resume = _get_owned_resume(db, resume_id, user)
    if not Path(resume.stored_path).exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File missing on disk")
    with open(resume.stored_path, "rb") as f:
        contents = f.read()
    resume = process_resume(db, resume, contents)
    return _resume_out(resume)


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(resume_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    resume = _get_owned_resume(db, resume_id, user)
    delete_file(resume.stored_path)
    db.delete(resume)
    db.commit()
    return None
