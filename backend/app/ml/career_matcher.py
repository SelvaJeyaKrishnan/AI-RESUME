"""
Career / job-eligibility matching.

Roles are defined as weighted skill profiles built from the same canonical
skill names the resume parser produces, so a match percentage is always
derived from skills actually detected in the user's resume — never guessed
or hardcoded per user.

Language is deliberately non-guaranteeing: we report alignment, not eligibility.
"""
from dataclasses import dataclass, field

# Each role: core skills (heavily weighted), supporting skills (lighter),
# and a rough expected experience floor in years.
ROLE_LIBRARY: dict[str, dict] = {
    "Python Developer": {
        "core": ["Python", "SQL", "Git", "REST API"],
        "supporting": ["Django", "Flask", "FastAPI", "PostgreSQL", "Docker", "Unit Testing"],
        "min_years": 1,
        "blurb": "Builds and maintains Python-based applications and services.",
    },
    "Backend Developer": {
        "core": ["REST API", "SQL", "Git"],
        "supporting": ["Python", "Node.js", "Java", "Go", "PostgreSQL", "MongoDB", "Redis", "Docker", "System Design"],
        "min_years": 1,
        "blurb": "Designs server-side services, APIs and data layers.",
    },
    "Frontend Developer": {
        "core": ["JavaScript", "React", "HTML/CSS", "Git"],
        "supporting": ["TypeScript", "Vue.js", "Angular", "Redux", "Next.js", "Tailwind CSS", "UI/UX Design"],
        "min_years": 1,
        "blurb": "Builds user-facing interfaces and client-side application logic.",
    },
    "Full-Stack Developer": {
        "core": ["JavaScript", "React", "REST API", "SQL", "Git"],
        "supporting": ["Python", "Node.js", "TypeScript", "PostgreSQL", "Docker", "HTML/CSS", "FastAPI", "Django"],
        "min_years": 2,
        "blurb": "Works across both frontend interfaces and backend services.",
    },
    "AI/ML Engineer": {
        "core": ["Python", "Machine Learning", "NumPy", "Pandas"],
        "supporting": ["TensorFlow", "PyTorch", "scikit-learn", "Deep Learning", "Natural Language Processing",
                        "Computer Vision", "LLM", "Docker", "AWS"],
        "min_years": 1,
        "blurb": "Builds, trains and deploys machine learning models into products.",
    },
    "Data Analyst": {
        "core": ["SQL", "Data Analysis", "Excel"],
        "supporting": ["Python", "R", "Pandas", "Data Visualization", "Big Data", "NumPy"],
        "min_years": 0,
        "blurb": "Turns raw data into reporting, dashboards and business insight.",
    },
    "Data Scientist": {
        "core": ["Python", "Machine Learning", "SQL", "Data Analysis"],
        "supporting": ["Pandas", "NumPy", "scikit-learn", "Data Visualization", "R", "Deep Learning", "Big Data"],
        "min_years": 2,
        "blurb": "Applies statistical and ML methods to answer business questions.",
    },
    "DevOps Engineer": {
        "core": ["Docker", "CI/CD", "Linux", "Git"],
        "supporting": ["Kubernetes", "AWS", "Azure", "Google Cloud", "Terraform", "Jenkins", "Python"],
        "min_years": 2,
        "blurb": "Automates build, deployment and infrastructure operations.",
    },
    "Cloud Engineer": {
        "core": ["AWS", "Linux", "Docker"],
        "supporting": ["Azure", "Google Cloud", "Kubernetes", "Terraform", "CI/CD", "Python", "System Design"],
        "min_years": 2,
        "blurb": "Designs and runs cloud infrastructure and deployment topologies.",
    },
    "Mobile App Developer": {
        "core": ["Git", "React Native", "Flutter", "iOS Development", "Android Development"],
        "supporting": ["Swift", "Kotlin", "JavaScript", "TypeScript", "REST API", "UI/UX Design"],
        "min_years": 1,
        "blurb": "Builds native or cross-platform mobile applications.",
        # At least one genuinely mobile skill is required for this to be a real match
        "distinctive": ["React Native", "Flutter", "iOS Development", "Android Development", "Swift", "Kotlin"],
    },
    "QA / Test Engineer": {
        # Testing alone isn't a QA role — every good engineer writes tests.
        # A real QA profile needs test strategy plus process skills.
        "core": ["Unit Testing", "CI/CD", "Agile/Scrum"],
        "supporting": ["Python", "JavaScript", "REST API", "Git", "Project Management"],
        "min_years": 0,
        "blurb": "Designs test strategy and automated test coverage for products.",
        "distinctive": ["Unit Testing"],
    },
    "Business / Product Analyst": {
        "core": ["Data Analysis", "Communication", "Excel"],
        "supporting": ["SQL", "Product Management", "Agile/Scrum", "Data Visualization", "Project Management"],
        "min_years": 0,
        "blurb": "Bridges business needs and delivery teams with data and requirements.",
    },
}


@dataclass
class RoleMatch:
    role: str
    blurb: str
    match_percent: float
    matching_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    experience_note: str = ""
    why: str = ""
    next_steps: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "role": self.role,
            "blurb": self.blurb,
            "match_percent": self.match_percent,
            "matching_skills": self.matching_skills,
            "missing_skills": self.missing_skills,
            "experience_note": self.experience_note,
            "why": self.why,
            "next_steps": self.next_steps,
        }


def _alignment_language(pct: float) -> str:
    if pct >= 80:
        return "Your resume currently shows strong alignment with this role."
    if pct >= 60:
        return "Your resume shows solid partial alignment with this role."
    if pct >= 40:
        return "Your resume shows some overlap with this role, with notable gaps."
    return "Your resume currently shows limited overlap with this role."


def match_roles(
    candidate_skills: set[str],
    years_of_experience: float,
    target_job_title: str | None = None,
    top_n: int = 5,
) -> list[RoleMatch]:
    """Score every role in the library against the skills actually found in the
    resume, and return the best-aligned ones."""
    results: list[RoleMatch] = []

    for role, spec in ROLE_LIBRARY.items():
        core = set(spec["core"])
        supporting = set(spec["supporting"])

        core_hit = core & candidate_skills
        supp_hit = supporting & candidate_skills

        core_ratio = len(core_hit) / len(core) if core else 0.0
        supp_ratio = len(supp_hit) / len(supporting) if supporting else 0.0

        # Coverage of the role's ENTIRE skill profile. Without this term, a role
        # with a short core list (e.g. two generic skills) can be "fully matched"
        # by almost any engineer and outrank a far more appropriate role.
        profile = core | supporting
        profile_ratio = len(profile & candidate_skills) / len(profile) if profile else 0.0

        # Core skills still matter most, but breadth across the whole profile
        # keeps small-core roles from dominating the ranking.
        skill_score = core_ratio * 0.45 + supp_ratio * 0.2 + profile_ratio * 0.35

        # Guard against generic skills (Git, SQL) inflating an unrelated role.
        # If a role declares distinctive skills and the candidate has none of
        # them, the match is capped — you are not a "Mobile App Developer"
        # match just because you use version control.
        distinctive = set(spec.get("distinctive", []))
        if distinctive and not (distinctive & candidate_skills):
            skill_score = min(skill_score, 0.25)

        # Experience acts as a modest modifier, never the whole story.
        min_years = spec["min_years"]
        if min_years <= 0:
            exp_modifier = 1.0
            exp_note = "This role is commonly open to early-career candidates."
        elif years_of_experience >= min_years:
            exp_modifier = 1.0
            exp_note = f"Your ~{years_of_experience:g} year(s) meets the ~{min_years}+ year level typically expected."
        else:
            exp_modifier = 0.82
            exp_note = (f"This role typically expects ~{min_years}+ year(s); your resume indicates "
                         f"~{years_of_experience:g}. Projects and internships can help bridge this.")

        match_percent = round(skill_score * exp_modifier * 100, 1)

        missing_core = sorted(core - candidate_skills)
        missing_supp = sorted(supporting - candidate_skills)
        missing = (missing_core + missing_supp)[:6]

        next_steps = []
        if missing_core:
            next_steps.append(f"Build and demonstrate the core skills first: {', '.join(missing_core[:3])}.")
        if missing_supp:
            next_steps.append(f"Then strengthen supporting tools: {', '.join(missing_supp[:3])}.")
        if years_of_experience < min_years:
            next_steps.append("Ship a substantial portfolio project to offset the experience gap.")
        if not next_steps:
            next_steps.append("Tailor your resume's summary and bullets specifically to this role's language.")

        results.append(RoleMatch(
            role=role,
            blurb=spec["blurb"],
            match_percent=match_percent,
            matching_skills=sorted(core_hit | supp_hit),
            missing_skills=missing,
            experience_note=exp_note,
            why=_alignment_language(match_percent),
            next_steps=next_steps,
        ))

    results.sort(key=lambda r: r.match_percent, reverse=True)

    # If the user named a target role, surface it even if it isn't top-ranked.
    if target_job_title:
        low = target_job_title.lower()
        for r in results:
            if r.role.lower() in low or any(w in low for w in r.role.lower().split()[:1]):
                if r not in results[:top_n]:
                    return [r] + results[: top_n - 1]
                break

    return results[:top_n]
