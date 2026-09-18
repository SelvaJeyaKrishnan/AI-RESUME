from sqlalchemy.orm import Session

from app.models.resume import Skill, CandidateSkill


def sync_candidate_skills(db: Session, candidate_id: str, skill_hits: dict[str, int]) -> None:
    """Ensure Skill rows exist for each detected skill, and link them to the candidate
    via CandidateSkill with a mention count. Clears previous links first (used on re-analyze)."""
    db.query(CandidateSkill).filter(CandidateSkill.candidate_id == candidate_id).delete()

    for name, count in skill_hits.items():
        skill = db.query(Skill).filter(Skill.name == name).first()
        if not skill:
            skill = Skill(name=name)
            db.add(skill)
            db.flush()  # get skill.id without a full commit
        db.add(CandidateSkill(candidate_id=candidate_id, skill_id=skill.id, mentions=count))

    db.commit()
