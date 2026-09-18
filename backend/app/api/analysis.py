from collections import Counter

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.jobs import _get_owned_job
from app.api.resumes import _get_owned_resume, _candidate_out
from app.database.session import get_db
from app.models.analysis import ResumeAnalysis
from app.models.resume import Resume, CandidateSkill, Skill
from app.models.user import User
from app.schemas.analysis import (
    AnalysisOut, RankedCandidateOut, ComparisonRequest, AnalyticsOut,
)
from app.services.analysis_service import run_analysis
from app.utils.json_utils import from_json

router = APIRouter(tags=["analysis"])


def _analysis_out(analysis: ResumeAnalysis) -> AnalysisOut:
    return AnalysisOut(
        id=analysis.id,
        resume_id=analysis.resume_id,
        job_id=analysis.job_id,
        overall_score=analysis.overall_score,
        skills_score=analysis.skills_score,
        experience_score=analysis.experience_score,
        semantic_score=analysis.semantic_score,
        education_score=analysis.education_score,
        keyword_score=analysis.keyword_score,
        matching_skills=from_json(analysis.matching_skills, []),
        missing_skills=from_json(analysis.missing_skills, []),
        strengths=from_json(analysis.strengths, []),
        gaps=from_json(analysis.gaps, []),
        ai_summary=analysis.ai_summary,
        recommendation=analysis.recommendation,
        analyzed_at=analysis.analyzed_at,
    )


@router.post("/analysis/{resume_id}/{job_id}", response_model=AnalysisOut)
def analyze_resume_for_job(resume_id: str, job_id: str, db: Session = Depends(get_db),
                            user: User = Depends(get_current_user)):
    resume = _get_owned_resume(db, resume_id, user)
    job = _get_owned_job(db, job_id, user)
    analysis = run_analysis(db, resume, job)
    return _analysis_out(analysis)


@router.get("/analysis/{resume_id}/{job_id}", response_model=AnalysisOut)
def get_analysis(resume_id: str, job_id: str, db: Session = Depends(get_db),
                  user: User = Depends(get_current_user)):
    _get_owned_resume(db, resume_id, user)
    _get_owned_job(db, job_id, user)
    analysis = (
        db.query(ResumeAnalysis)
        .filter(ResumeAnalysis.resume_id == resume_id, ResumeAnalysis.job_id == job_id)
        .first()
    )
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
    return _analysis_out(analysis)


def _ranked_candidates(db: Session, job_id: str) -> list[RankedCandidateOut]:
    analyses = (
        db.query(ResumeAnalysis)
        .filter(ResumeAnalysis.job_id == job_id)
        .order_by(ResumeAnalysis.overall_score.desc())
        .all()
    )
    out = []
    for a in analyses:
        resume = db.query(Resume).filter(Resume.id == a.resume_id).first()
        if not resume:
            continue
        out.append(RankedCandidateOut(
            resume_id=resume.id,
            analysis=_analysis_out(a),
            candidate=_candidate_out(resume.candidate),
            original_filename=resume.original_filename,
        ))
    return out


@router.get("/jobs/{job_id}/candidates", response_model=list[RankedCandidateOut])
def get_job_candidates(job_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _get_owned_job(db, job_id, user)
    return _ranked_candidates(db, job_id)


@router.get("/jobs/{job_id}/ranking", response_model=list[RankedCandidateOut])
def get_job_ranking(job_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Alias of /candidates, explicitly sorted highest-to-lowest score (same ordering)."""
    _get_owned_job(db, job_id, user)
    return _ranked_candidates(db, job_id)


@router.post("/jobs/{job_id}/compare", response_model=list[RankedCandidateOut])
def compare_candidates(job_id: str, payload: ComparisonRequest, db: Session = Depends(get_db),
                        user: User = Depends(get_current_user)):
    _get_owned_job(db, job_id, user)
    if not (2 <= len(payload.resume_ids) <= 3):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail="Select 2 or 3 candidates to compare")
    ranked = _ranked_candidates(db, job_id)
    selected = [r for r in ranked if r.resume_id in payload.resume_ids]
    if len(selected) != len(payload.resume_ids):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail="One or more candidates have not been analyzed for this job")
    return selected


@router.get("/jobs/{job_id}/analytics", response_model=AnalyticsOut)
def job_analytics(job_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    job = _get_owned_job(db, job_id, user)
    analyses = db.query(ResumeAnalysis).filter(ResumeAnalysis.job_id == job.id).all()
    all_resumes = db.query(Resume).filter(Resume.owner_id == user.id).count()
    failed = db.query(Resume).filter(Resume.owner_id == user.id, Resume.parse_status == "failed").count()

    total = len(analyses)
    avg_score = round(sum(a.overall_score for a in analyses) / total, 1) if total else 0.0
    shortlisted = sum(1 for a in analyses if a.recommendation in ("Strong Match", "Good Match"))

    buckets = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
    for a in analyses:
        s = a.overall_score
        if s <= 20:
            buckets["0-20"] += 1
        elif s <= 40:
            buckets["21-40"] += 1
        elif s <= 60:
            buckets["41-60"] += 1
        elif s <= 80:
            buckets["61-80"] += 1
        else:
            buckets["81-100"] += 1

    rec_breakdown = dict(Counter(a.recommendation for a in analyses))

    # top skills across candidates who were analyzed for this job
    resume_ids = [a.resume_id for a in analyses]
    skill_counter: Counter = Counter()
    if resume_ids:
        resumes = db.query(Resume).filter(Resume.id.in_(resume_ids)).all()
        candidate_ids = [r.candidate.id for r in resumes if r.candidate]
        if candidate_ids:
            links = db.query(CandidateSkill).filter(CandidateSkill.candidate_id.in_(candidate_ids)).all()
            skill_ids = [link.skill_id for link in links]
            skills = db.query(Skill).filter(Skill.id.in_(skill_ids)).all()
            id_to_name = {s.id: s.name for s in skills}
            for link in links:
                skill_counter[id_to_name.get(link.skill_id, "Unknown")] += 1

    top_skills = [{"skill": name, "count": count} for name, count in skill_counter.most_common(10)]

    return AnalyticsOut(
        total_candidates=total,
        processed_resumes=all_resumes - failed,
        failed_resumes=failed,
        shortlisted_candidates=shortlisted,
        average_match_score=avg_score,
        score_distribution=buckets,
        recommendation_breakdown=rec_breakdown,
        top_skills=top_skills,
    )
