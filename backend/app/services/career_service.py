"""
Builds a complete candidate-facing career report by composing the existing
matching engine with the ATS scorer, career matcher and tips engine.

Reuses (does not duplicate) the resume parsing and matching pipeline that
already powers the recruiter flow.
"""
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.ml.ats_scorer import compute_ats_score, detect_content_quality
from app.ml.career_matcher import match_roles
from app.ml.improvement_tips import generate_tips
from app.ml.skill_extractor import extract_skills
from app.models.career import CareerReport
from app.models.job import Job
from app.models.resume import Resume
from app.services.analysis_service import run_analysis, _candidate_to_parsed, _job_to_parsed
from app.utils.json_utils import to_json, from_json


def _build_category_ratings(analysis, ats, content_score, content_notes, candidate) -> list[dict]:
    """The overall resume rating, broken into explainable categories.
    Every score here traces back to a real computed value."""
    def suggestion_for(score: float, good: str, bad: str) -> str:
        return good if score >= 70 else bad

    return [
        {
            "key": "ats",
            "label": "ATS Compatibility",
            "score": ats.overall,
            "explanation": "How reliably an applicant tracking system can parse and rank your resume.",
            "suggestion": suggestion_for(
                ats.overall,
                "Your resume should parse cleanly in most ATS pipelines.",
                "Simplify layout and add clearly labelled sections to improve machine readability.",
            ),
        },
        {
            "key": "skills",
            "label": "Skills",
            "score": analysis.skills_score,
            "explanation": "How well the skills detected in your resume cover what the target job asks for.",
            "suggestion": suggestion_for(
                analysis.skills_score,
                "Your skill coverage against this role is solid.",
                "Name the required technologies explicitly where you've genuinely used them.",
            ),
        },
        {
            "key": "experience",
            "label": "Experience",
            "score": analysis.experience_score,
            "explanation": "How your detected years of experience compare with the role's stated expectation.",
            "suggestion": suggestion_for(
                analysis.experience_score,
                "Your experience level lines up with this role.",
                "Surface internships, freelance work and substantial projects to strengthen this.",
            ),
        },
        {
            "key": "education",
            "label": "Education",
            "score": analysis.education_score,
            "explanation": "Whether your education matches the qualification the job description mentions.",
            "suggestion": suggestion_for(
                analysis.education_score,
                "Your education matches what this role asks for.",
                "State your degree, field and graduation year on a clearly labelled line.",
            ),
        },
        {
            "key": "projects",
            "label": "Project Relevance",
            "score": round(min(100.0, len(candidate.projects) * 25 + (25 if candidate.projects else 0)), 1),
            "explanation": "How much concrete project evidence your resume presents.",
            "suggestion": suggestion_for(
                len(candidate.projects) * 25,
                "You present a good amount of project evidence.",
                "Add 2–3 projects with the problem, your stack, your role and a link.",
            ),
        },
        {
            "key": "content",
            "label": "Content Quality",
            "score": content_score,
            "explanation": "Writing strength: action verbs, quantified achievements and a clear summary.",
            "suggestion": " ".join(content_notes[:2]) if content_notes else "Content reads well.",
        },
        {
            "key": "alignment",
            "label": "Job Alignment",
            "score": analysis.semantic_score,
            "explanation": "Overall language and semantic similarity between your resume and the target job.",
            "suggestion": suggestion_for(
                analysis.semantic_score,
                "Your resume speaks this role's language.",
                "Mirror more of the job description's terminology in your summary and bullets.",
            ),
        },
    ]


def build_career_report(db: Session, resume: Resume, job: Job, owner_id: str) -> CareerReport:
    """Run the full candidate-facing analysis and persist it as a CareerReport."""
    # 1. Reuse the existing matching engine for the core scores
    analysis = run_analysis(db, resume, job)

    candidate = resume.candidate
    parsed_candidate = _candidate_to_parsed(candidate)
    parsed_job = _job_to_parsed(job)

    resume_text = resume.raw_text or ""
    candidate_skills = set(extract_skills(resume_text).keys())

    # 2. ATS scoring (transparent, factor-by-factor)
    ats = compute_ats_score(
        resume_text=resume_text,
        candidate=parsed_candidate,
        candidate_skills=candidate_skills,
        job=parsed_job,
        semantic_score=analysis.semantic_score,
    )
    ats_factor_scores = {f.key: f.score for f in ats.factors}

    # 3. Content quality
    content_score, content_notes = detect_content_quality(resume_text)

    # 4. Category ratings -> overall resume score
    ratings = _build_category_ratings(analysis, ats, content_score, content_notes, parsed_candidate)
    overall_score = round(sum(r["score"] for r in ratings) / len(ratings), 1)

    # 5. Career role matching from real extracted skills
    roles = match_roles(
        candidate_skills=candidate_skills,
        years_of_experience=parsed_candidate.years_of_experience,
        target_job_title=job.title,
    )

    # 6. Skill gap analysis
    required = set(parsed_job.required_skills)
    preferred = set(parsed_job.preferred_skills)
    skill_gap = {
        "have": sorted(candidate_skills),
        "required_by_job": sorted(required),
        "preferred_by_job": sorted(preferred),
        "missing_required": sorted(required - candidate_skills),
        "missing_preferred": sorted(preferred - candidate_skills),
        "matched": sorted((required | preferred) & candidate_skills),
        "parser_caveat": (
            "These are the skills our parser could detect in your resume text. "
            "If you have a skill that isn't listed here, it may simply not have been "
            "written explicitly enough for an ATS to detect it — which is itself worth fixing."
        ),
    }

    # 7. Improvement tips from real detected issues
    tips = generate_tips(resume_text, parsed_candidate, candidate_skills, parsed_job, ats_factor_scores)

    # 8. Strengths / weaknesses derived from the computed ratings
    strengths = [f"{r['label']}: {round(r['score'])}/100 — {r['explanation']}"
                  for r in sorted(ratings, key=lambda x: -x["score"]) if r["score"] >= 70][:5]
    weaknesses = [f"{r['label']}: {round(r['score'])}/100 — {r['suggestion']}"
                   for r in sorted(ratings, key=lambda x: x["score"]) if r["score"] < 70][:5]
    if not strengths:
        strengths = ["Your resume parsed successfully, which means an ATS can read it — that's the baseline."]

    report = CareerReport(
        owner_id=owner_id,
        resume_id=resume.id,
        job_id=job.id,
        target_job_description=job.description_raw,
        ats_payload=to_json(ats.as_dict()),
        ratings_payload=to_json(ratings),
        roles_payload=to_json([r.as_dict() for r in roles]),
        skill_gap_payload=to_json(skill_gap),
        tips_payload=to_json([t.as_dict() for t in tips]),
        strengths=to_json(strengths),
        weaknesses=to_json(weaknesses),
        overall_score=overall_score,
        ats_score=ats.overall,
        job_match_score=analysis.overall_score,
        status="awaiting_assessment",
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def serialize_report(db: Session, report: CareerReport) -> dict:
    """Full report payload for the frontend (only served once unlocked)."""
    resume = db.query(Resume).filter(Resume.id == report.resume_id).first()
    job = db.query(Job).filter(Job.id == report.job_id).first()
    candidate = resume.candidate if resume else None
    assessment = report.assessment

    return {
        "id": report.id,
        "status": report.status,
        "created_at": report.created_at,
        "target_job_title": job.title if job else None,
        "target_job_description": report.target_job_description,
        "resume": {
            "id": resume.id if resume else None,
            "filename": resume.original_filename if resume else None,
            "text_preview": (resume.raw_text[:4000] if resume and resume.raw_text else None),
        },
        "candidate": {
            "full_name": candidate.full_name if candidate else None,
            "email": candidate.email if candidate else None,
            "phone": candidate.phone if candidate else None,
            "location": candidate.location if candidate else None,
            "years_of_experience": candidate.years_of_experience if candidate else 0,
            "education": from_json(candidate.education, []) if candidate else [],
            "projects": from_json(candidate.projects, []) if candidate else [],
            "certifications": from_json(candidate.certifications, []) if candidate else [],
            "skills": [l.skill.name for l in candidate.skills] if candidate and candidate.skills else [],
        } if candidate else None,
        "overall_score": report.overall_score,
        "ats_score": report.ats_score,
        "job_match_score": report.job_match_score,
        "ats": from_json(report.ats_payload, {}),
        "ratings": from_json(report.ratings_payload, []),
        "roles": from_json(report.roles_payload, []),
        "skill_gap": from_json(report.skill_gap_payload, {}),
        "tips": from_json(report.tips_payload, []),
        "strengths": from_json(report.strengths, []),
        "weaknesses": from_json(report.weaknesses, []),
        "communication": {
            "correct": assessment.correct_count,
            "total": assessment.total_questions,
            "accuracy": assessment.accuracy,
            "band": assessment.band,
            "message": assessment.band_message,
        } if assessment and assessment.completed else None,
        "disclaimer": (
            "This report is generated by automated analysis of your resume text against the job "
            "description you provided. Scores are AI-generated assessments intended to guide your "
            "improvements — they are not a hiring decision, a guarantee of eligibility, or a "
            "definitive evaluation of your ability."
        ),
    }
