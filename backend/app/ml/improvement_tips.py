"""
Personalised resume improvement tips.

Each tip is only emitted when the corresponding issue is actually detected
in the user's resume text / parsed entities / JD comparison. Tips carry the
issue, why it matters, and a concrete fix — with a real before/after example
pulled from the user's own resume wherever we can find one.
"""
import re
from dataclasses import dataclass, field

from app.ml.ats_scorer import WEAK_VERBS, QUANTIFIED_RE, BULLET_RE
from app.ml.jd_parser import ParsedJob
from app.ml.resume_parser import ParsedCandidate


@dataclass
class ImprovementTip:
    title: str
    issue: str
    why: str
    fix: str
    priority: str = "medium"  # high | medium | low
    before: str | None = None
    after: str | None = None

    def as_dict(self) -> dict:
        return {
            "title": self.title, "issue": self.issue, "why": self.why, "fix": self.fix,
            "priority": self.priority, "before": self.before, "after": self.after,
        }


def _find_weak_bullet(resume_text: str) -> str | None:
    """Return an actual line from the resume that uses passive phrasing."""
    for line in resume_text.splitlines():
        stripped = line.strip(" \t•-*")
        low = stripped.lower()
        if any(v in low for v in WEAK_VERBS) and 20 < len(stripped) < 180:
            return stripped
    return None


def _rewrite_weak_bullet(bullet: str) -> str:
    """Produce an illustrative stronger rewrite of the user's own bullet."""
    rewritten = bullet
    replacements = {
        "responsible for": "Led",
        "was responsible for": "Led",
        "worked on": "Built",
        "helped with": "Contributed to",
        "involved in": "Delivered",
        "duties included": "Owned",
        "assisted with": "Supported",
    }
    low = rewritten.lower()
    for weak, strong in replacements.items():
        idx = low.find(weak)
        if idx != -1:
            rewritten = rewritten[:idx] + strong + rewritten[idx + len(weak):]
            break
    rewritten = rewritten[0].upper() + rewritten[1:] if rewritten else rewritten
    if not QUANTIFIED_RE.search(rewritten):
        rewritten = rewritten.rstrip(".") + ", reducing manual effort by ~30% (replace with your real metric)."
    return rewritten


def generate_tips(
    resume_text: str,
    candidate: ParsedCandidate,
    candidate_skills: set[str],
    job: ParsedJob,
    ats_factor_scores: dict[str, float],
) -> list[ImprovementTip]:
    tips: list[ImprovementTip] = []
    low = resume_text.lower()

    # 1. Professional summary
    if not re.search(r"(?im)^\s*(summary|profile|objective|about me)\s*:?\s*$", resume_text):
        tips.append(ImprovementTip(
            title="Add a professional summary",
            issue="No summary or profile section was detected at the top of your resume.",
            why="Recruiters and ATS systems both read the top of the resume first. A 2–3 line summary "
                 "frames your experience before anyone reaches your bullet points.",
            fix=f"Add a short summary naming your role, your years of experience, and 3–4 core technologies"
                 f"{' relevant to ' + job.title if job.title else ''}.",
            priority="high",
            after=(f"{candidate.full_name or 'Your name'} — "
                    f"{'Developer' if not job.title else job.title} with {candidate.years_of_experience:g}+ years "
                    f"building {', '.join(sorted(candidate_skills)[:3]) or 'software'}. "
                    f"Focused on shipping reliable, well-tested work."),
        ))

    # 2. Quantified achievements
    quantified = len(QUANTIFIED_RE.findall(resume_text))
    if quantified < 3:
        weak = _find_weak_bullet(resume_text)
        tips.append(ImprovementTip(
            title="Add measurable achievements",
            issue=f"Only {quantified} quantified detail(s) were detected across your resume.",
            why="Numbers turn responsibilities into evidence. 'Improved performance' is a claim; "
                 "'cut page load from 4s to 1.2s' is proof.",
            fix="Add a metric to each major bullet — scale (users, requests, records), impact (%, time saved), "
                 "or scope (team size, systems owned).",
            priority="high",
            before=weak,
            after=_rewrite_weak_bullet(weak) if weak else None,
        ))

    # 3. Passive phrasing
    weak_hits = [v for v in WEAK_VERBS if v in low]
    if weak_hits:
        weak_line = _find_weak_bullet(resume_text)
        tips.append(ImprovementTip(
            title="Replace passive phrasing with action verbs",
            issue=f"Your resume uses passive constructions such as: {', '.join(weak_hits[:3])}.",
            why="Passive phrasing describes a job description rather than your contribution. "
                 "Action verbs signal ownership.",
            fix="Start each bullet with a strong verb: Built, Designed, Led, Automated, Reduced, Shipped, Migrated.",
            priority="medium",
            before=weak_line,
            after=_rewrite_weak_bullet(weak_line) if weak_line else None,
        ))

    # 4. Missing JD keywords
    missing_required = sorted(set(job.required_skills) - candidate_skills)
    if missing_required:
        tips.append(ImprovementTip(
            title="Include relevant keywords from the target job",
            issue=f"The job description asks for {', '.join(missing_required[:5])}, which weren't detected in your resume.",
            why="Most ATS filters rank on keyword overlap before a human ever reads the resume. "
                 "Skills you have but didn't name are invisible to them.",
            fix="If you genuinely have any of these, name them explicitly in your skills section and in the "
                 "bullet where you used them. Don't claim skills you don't have — recruiters probe them at interview.",
            priority="high",
        ))

    # 5. Bullet structure
    if len(BULLET_RE.findall(resume_text)) < 3:
        tips.append(ImprovementTip(
            title="Improve bullet-point structure",
            issue="Very few bullet points were detected — your experience may be written as dense paragraphs.",
            why="Recruiters scan resumes in seconds, and ATS parsers segment bullets more reliably than prose.",
            fix="Break each role into 3–5 bullets following: action verb → what you built → technology → measurable result.",
            priority="medium",
        ))

    # 6. Skills section
    if not re.search(r"(?im)^\s*(skills|technical skills|core competencies)\s*:?\s*$", resume_text):
        tips.append(ImprovementTip(
            title="Add a dedicated skills section",
            issue="No clearly labelled skills section was detected.",
            why="A labelled skills block is one of the most reliably parsed sections in any ATS.",
            fix="Add a 'Skills' heading grouping your technologies by category (languages, frameworks, tools, cloud).",
            priority="high" if not candidate_skills else "medium",
        ))

    # 7. Contact details
    missing_contact = [label for label, val in
                        (("email address", candidate.email), ("phone number", candidate.phone)) if not val]
    if missing_contact:
        tips.append(ImprovementTip(
            title="Make your contact details machine-readable",
            issue=f"Could not parse your {', '.join(missing_contact)} from the resume.",
            why="If an ATS can't extract your contact details, your application can be filtered out before review.",
            fix="Put contact details as plain text on their own lines at the top — not inside a header, image, or table.",
            priority="high",
        ))

    # 8. ATS formatting
    if ats_factor_scores.get("formatting", 100) < 75:
        tips.append(ImprovementTip(
            title="Improve ATS readability",
            issue="Formatting patterns were detected that commonly break ATS text extraction.",
            why="Multi-column layouts, tables, text boxes and icon fonts frequently scramble or drop content entirely.",
            fix="Export a single-column version in a standard font, with plain bullets and plain text headings, "
                 "and keep the designed version for direct human applications.",
            priority="medium",
        ))

    # 9. Length
    words = len(resume_text.split())
    if words < 200:
        tips.append(ImprovementTip(
            title="Expand your resume content",
            issue=f"Your resume is quite short (~{words} words).",
            why="A thin resume gives neither a recruiter nor an ATS enough signal to rank you.",
            fix="Expand projects with context: the problem, your approach, the technology, and the outcome.",
            priority="high",
        ))
    elif words > 1200:
        tips.append(ImprovementTip(
            title="Tighten your resume",
            issue=f"Your resume is long (~{words} words).",
            why="Long resumes dilute your strongest material.",
            fix="Cut older or less relevant roles down to one line each and keep detail on the last 2–3 roles.",
            priority="low",
        ))

    # 10. Projects (valuable for early-career candidates)
    if candidate.years_of_experience < 2 and len(candidate.projects) < 2:
        tips.append(ImprovementTip(
            title="Add more substantial projects",
            issue="Few projects were detected, and your experience level is early-career.",
            why="With limited work history, projects are the main evidence a recruiter has of what you can build.",
            fix="Add 2–3 projects with a one-line problem statement, the stack used, your specific role, "
                 "and a live link or repository.",
            priority="high",
        ))

    priority_rank = {"high": 0, "medium": 1, "low": 2}
    tips.sort(key=lambda t: priority_rank.get(t.priority, 1))
    return tips
