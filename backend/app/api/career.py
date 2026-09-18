from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.ml.assessment_bank import build_assessment, public_question, score_band
from app.models.career import CareerReport, Assessment
from app.models.job import Job
from app.models.resume import Resume
from app.models.user import User
from app.services.career_service import build_career_report, serialize_report
from app.services.job_service import populate_job_from_description
from app.services.resume_service import process_resume
from app.utils.file_handling import validate_file, compute_file_hash, save_upload
from app.utils.json_utils import to_json, from_json

router = APIRouter(prefix="/career", tags=["career"])


def _get_owned_report(db: Session, report_id: str, user: User) -> CareerReport:
    report = (
        db.query(CareerReport)
        .filter(CareerReport.id == report_id, CareerReport.owner_id == user.id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return report


@router.post("/reports", status_code=status.HTTP_201_CREATED)
async def create_career_report(
    file: UploadFile = File(...),
    job_description: str = Form(...),
    job_title: str | None = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Upload a resume + target job description, run the full analysis, and create
    a report that stays LOCKED until the communication assessment is completed."""
    if not job_description or len(job_description.strip()) < 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please describe the role you're targeting in a bit more detail (at least 20 characters).",
        )

    contents = await file.read()
    ext = validate_file(file, contents)  # raises friendly 415/413/400 on bad input

    # Store + parse the resume (reuses the existing pipeline)
    stored_path = save_upload(contents, ext, user.id)
    resume = Resume(
        owner_id=user.id,
        original_filename=file.filename or "resume",
        stored_path=stored_path,
        file_type=ext.lstrip("."),
        file_hash=compute_file_hash(contents),
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    resume = process_resume(db, resume, contents)
    if resume.parse_status != "success":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"We couldn't read that resume: {resume.parse_error or 'unknown parsing error'}. "
                    f"Try exporting it as a text-based PDF or DOCX rather than a scan or image.",
        )

    # Create the target job from the description the user typed
    job = Job(owner_id=user.id, title=job_title or "", description_raw=job_description, status="target")
    job = populate_job_from_description(job)
    db.add(job)
    db.commit()
    db.refresh(job)

    # Run the full analysis, but keep it locked
    report = build_career_report(db, resume, job, owner_id=user.id)

    # Build the assessment up-front and store it server-side
    questions = build_assessment(seed=report.id)
    assessment = Assessment(
        report_id=report.id,
        questions_payload=to_json(questions),
        total_questions=len(questions),
    )
    db.add(assessment)
    db.commit()

    # Deliberately return NO scores here — the report is gated.
    return {
        "report_id": report.id,
        "status": report.status,
        "candidate_name": resume.candidate.full_name if resume.candidate else None,
        "target_job_title": job.title,
        "total_questions": len(questions),
        "message": "Resume processed. Complete the communication assessment to unlock your career report.",
    }


@router.get("/reports/{report_id}/assessment")
def get_assessment(report_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Return the assessment questions WITHOUT correct answers or explanations."""
    report = _get_owned_report(db, report_id, user)
    assessment = report.assessment
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")

    questions = from_json(assessment.questions_payload, [])
    answers = from_json(assessment.answers_payload, {}) or {}

    return {
        "report_id": report.id,
        "completed": assessment.completed,
        "total": assessment.total_questions,
        "answered": len(answers),
        "questions": [public_question(q, i + 1, len(questions)) for i, q in enumerate(questions)],
    }


@router.post("/reports/{report_id}/assessment/answer")
def submit_answer(
    report_id: str,
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Submit one answer. Returns whether it was correct plus the explanation —
    this is the ONLY point at which the correct answer is revealed."""
    report = _get_owned_report(db, report_id, user)
    assessment = report.assessment
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    if assessment.completed:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                             detail="This assessment has already been completed.")

    question_id = payload.get("question_id")
    option_id = payload.get("option_id")
    if not question_id or not option_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail="Both question_id and option_id are required.")

    questions = from_json(assessment.questions_payload, [])
    question = next((q for q in questions if q["id"] == question_id), None)
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not part of this assessment.")

    answers = from_json(assessment.answers_payload, {}) or {}
    if question_id in answers:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                             detail="You've already answered this question.")

    answers[question_id] = option_id
    assessment.answers_payload = to_json(answers)
    db.add(assessment)
    db.commit()

    is_correct = option_id == question["correct"]
    correct_option = next((o for o in question["options"] if o["id"] == question["correct"]), None)
    selected_option = next((o for o in question["options"] if o["id"] == option_id), None)

    return {
        "correct": is_correct,
        "correct_option_id": question["correct"],
        "correct_option_text": correct_option["text"] if correct_option else None,
        "selected_option_text": selected_option["text"] if selected_option else None,
        "explanation": question["explanation"],
        "skill": question["skill"],
        "answered": len(answers),
        "total": assessment.total_questions,
        "feedback_title": "Correct! Great job." if is_correct else "Keep learning — this is an area you can improve.",
    }


@router.post("/reports/{report_id}/assessment/complete")
def complete_assessment(report_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Finalise the assessment, compute the communication score, and unlock the report."""
    report = _get_owned_report(db, report_id, user)
    assessment = report.assessment
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")

    # Idempotent: completing twice returns the same result rather than erroring
    if assessment.completed:
        return {
            "correct": assessment.correct_count,
            "total": assessment.total_questions,
            "accuracy": assessment.accuracy,
            "band": assessment.band,
            "message": assessment.band_message,
            "report_id": report.id,
            "already_completed": True,
        }

    questions = from_json(assessment.questions_payload, [])
    answers = from_json(assessment.answers_payload, {}) or {}

    if len(answers) < len(questions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Please answer all {len(questions)} questions before finishing "
                    f"({len(answers)} answered so far).",
        )

    correct = sum(1 for q in questions if answers.get(q["id"]) == q["correct"])
    accuracy = round(correct / len(questions) * 100, 1) if questions else 0.0
    band, message = score_band(correct, len(questions))

    assessment.correct_count = correct
    assessment.accuracy = accuracy
    assessment.band = band
    assessment.band_message = message
    assessment.completed = True
    assessment.completed_at = datetime.now(timezone.utc)

    report.status = "complete"
    report.unlocked_at = datetime.now(timezone.utc)

    db.add(assessment)
    db.add(report)
    db.commit()

    return {
        "correct": correct,
        "total": len(questions),
        "accuracy": accuracy,
        "band": band,
        "message": message,
        "report_id": report.id,
        "already_completed": False,
    }


@router.get("/reports/{report_id}")
def get_report(report_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Return the full career report — only if the assessment has been completed."""
    report = _get_owned_report(db, report_id, user)

    if report.status != "complete":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Complete the communication assessment to unlock this report.",
        )

    return serialize_report(db, report)


@router.get("/reports")
def list_reports(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """List the user's past reports (summary only)."""
    reports = (
        db.query(CareerReport)
        .filter(CareerReport.owner_id == user.id)
        .order_by(CareerReport.created_at.desc())
        .all()
    )
    out = []
    for r in reports:
        job = db.query(Job).filter(Job.id == r.job_id).first()
        out.append({
            "id": r.id,
            "status": r.status,
            "created_at": r.created_at,
            "target_job_title": job.title if job else None,
            # Scores only exposed for unlocked reports
            "overall_score": r.overall_score if r.status == "complete" else None,
            "ats_score": r.ats_score if r.status == "complete" else None,
            "job_match_score": r.job_match_score if r.status == "complete" else None,
        })
    return out


@router.delete("/reports/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(report_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    report = _get_owned_report(db, report_id, user)
    db.delete(report)
    db.commit()
    return None
