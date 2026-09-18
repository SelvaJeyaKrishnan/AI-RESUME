"""
Rule/regex-based structured entity extraction from raw resume text.
This intentionally avoids depending on a hosted NER API so the whole
pipeline runs locally; it favors robustness over perfect accuracy since
resumes are extremely varied in layout.
"""
import re
from dataclasses import dataclass, field

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(
    r"(?:(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{3,4})"
)
LINKEDIN_RE = re.compile(r"(?:linkedin\.com/in/[A-Za-z0-9\-_/]+)", re.IGNORECASE)

DEGREE_KEYWORDS = [
    "bachelor", "b.tech", "btech", "b.sc", "bsc", "b.e", "be ", "master",
    "m.tech", "mtech", "m.sc", "msc", "mba", "phd", "ph.d", "doctorate",
    "associate degree", "diploma", "b.com", "bca", "mca",
]

EDU_KEYWORD_RE = re.compile(
    r"(?im)^.*(" + "|".join(re.escape(k) for k in DEGREE_KEYWORDS) + r").*$"
)

SECTION_HEADERS = {
    "experience": r"(work experience|professional experience|experience|employment history)",
    "education": r"(education|academic background|qualifications)",
    "projects": r"(projects|personal projects|academic projects)",
    "certifications": r"(certifications?|licenses?)",
    "skills": r"(skills|technical skills|core competencies)",
}

JOB_TITLE_HINTS = [
    "engineer", "developer", "manager", "analyst", "scientist", "designer",
    "consultant", "architect", "lead", "director", "specialist", "intern",
    "administrator", "officer", "executive", "coordinator",
]


@dataclass
class ParsedCandidate:
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    education: list[dict] = field(default_factory=list)
    work_experience: list[dict] = field(default_factory=list)
    years_of_experience: float = 0.0
    projects: list[dict] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    job_titles: list[str] = field(default_factory=list)


def parse_resume(text: str) -> ParsedCandidate:
    candidate = ParsedCandidate()
    if not text or not text.strip():
        return candidate

    lines = [l.strip() for l in text.splitlines()]
    non_empty_lines = [l for l in lines if l.strip()]

    candidate.email = _first_match(EMAIL_RE, text)
    candidate.phone = _extract_phone(text)
    candidate.full_name = _guess_name(non_empty_lines, candidate.email)
    candidate.location = _guess_location(text)

    sections = _split_sections(text)

    candidate.education = _extract_education(sections.get("education", text))
    candidate.work_experience = _extract_experience(sections.get("experience", text))
    candidate.years_of_experience = _estimate_years_of_experience(
        text, candidate.work_experience
    )
    candidate.projects = _extract_projects(sections.get("projects", ""))
    candidate.certifications = _extract_certifications(sections.get("certifications", ""))
    candidate.job_titles = _extract_job_titles(text)

    return candidate


# ---------- helpers ----------

def _first_match(pattern: re.Pattern, text: str) -> str | None:
    m = pattern.search(text)
    return m.group(0) if m else None


def _extract_phone(text: str) -> str | None:
    for match in PHONE_RE.finditer(text):
        digits = re.sub(r"\D", "", match.group(0))
        if 7 <= len(digits) <= 15:
            return match.group(0).strip()
    return None


def _guess_name(lines: list[str], email: str | None) -> str | None:
    """Heuristic: the name is usually one of the first few non-empty lines,
    short, title-cased, without digits/emails/typical header words."""
    header_words = {"resume", "cv", "curriculum vitae", "profile"}
    for line in lines[:6]:
        candidate_line = line.strip()
        low = candidate_line.lower()
        if not candidate_line or low in header_words:
            continue
        if EMAIL_RE.search(candidate_line) or PHONE_RE.search(candidate_line):
            continue
        if any(ch.isdigit() for ch in candidate_line):
            continue
        words = candidate_line.split()
        if 1 <= len(words) <= 4 and all(w[0:1].isupper() or not w.isalpha() for w in words):
            return candidate_line
    return None


def _guess_location(text: str) -> str | None:
    # Look for "City, ST" / "City, Country" patterns near the top of the resume
    top_text = "\n".join(text.splitlines()[:15])
    match = re.search(r"\b([A-Z][a-zA-Z.]+(?:\s[A-Z][a-zA-Z.]+)?,\s?[A-Z]{2,}[a-zA-Z]*)\b", top_text)
    return match.group(1) if match else None


def _split_sections(text: str) -> dict[str, str]:
    """Split resume text into sections based on common headers."""
    markers = []
    for name, pattern in SECTION_HEADERS.items():
        for m in re.finditer(rf"(?im)^\s*{pattern}\s*:?\s*$", text):
            markers.append((m.start(), name))
    markers.sort()

    sections: dict[str, str] = {}
    for i, (start, name) in enumerate(markers):
        end = markers[i + 1][0] if i + 1 < len(markers) else len(text)
        sections[name] = text[start:end]
    return sections


def _extract_education(section_text: str) -> list[dict]:
    results = []
    for match in EDU_KEYWORD_RE.finditer(section_text):
        line = match.group(0).strip()
        if not line:
            continue
        year_match = re.search(r"(19|20)\d{2}", line)
        results.append({
            "degree_line": line[:200],
            "year": year_match.group(0) if year_match else None,
        })
        if len(results) >= 6:
            break
    return results


DATE_RANGE_RE = re.compile(
    r"(?P<start>(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*(19|20)\d{2}|(19|20)\d{2})"
    r"\s*(?:-|–|to)\s*"
    r"(?P<end>present|current|(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*(19|20)\d{2}|(19|20)\d{2})",
    re.IGNORECASE,
)


def _extract_experience(section_text: str) -> list[dict]:
    entries = []
    for match in DATE_RANGE_RE.finditer(section_text):
        line_start = section_text.rfind("\n", 0, match.start()) + 1
        line_end = section_text.find("\n", match.end())
        line_end = line_end if line_end != -1 else len(section_text)
        context = section_text[line_start:line_end].strip()
        entries.append({
            "date_range": match.group(0),
            "context": context[:200],
        })
        if len(entries) >= 10:
            break
    return entries


def _estimate_years_of_experience(full_text: str, work_experience: list[dict]) -> float:
    # 1) Prefer an explicit "X years of experience" statement if present
    explicit = re.search(r"(\d+(?:\.\d+)?)\+?\s*years?\s+(?:of\s+)?experience", full_text, re.IGNORECASE)
    if explicit:
        try:
            return float(explicit.group(1))
        except ValueError:
            pass

    # 2) Otherwise sum up date ranges found in the experience section.
    #    Month resolution matters: a Jun 2023 - Dec 2023 internship is 6 months
    #    of real experience, not zero.
    total_months = 0
    import datetime
    now = datetime.datetime.now()

    for entry in work_experience:
        m = DATE_RANGE_RE.search(entry.get("date_range", ""))
        if not m:
            continue

        start_year, start_month = _parse_year_month(m.group("start"))
        if start_year is None:
            continue

        end_str = m.group("end").lower()
        if "present" in end_str or "current" in end_str:
            end_year, end_month = now.year, now.month
        else:
            end_year, end_month = _parse_year_month(end_str)
            if end_year is None:
                end_year, end_month = start_year, start_month

        months = (end_year - start_year) * 12 + (end_month - start_month)
        # A single-month or same-month range still represents real tenure
        total_months += max(months, 1) if months >= 0 else 0

    return round(total_months / 12, 1) if total_months else 0.0


MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def _parse_year_month(text: str) -> tuple[int | None, int]:
    """Extract (year, month) from a date fragment like 'Jun 2023' or '2023'.
    Defaults the month to January when only a year is present."""
    if not text:
        return None, 1
    year_match = re.search(r"(19|20)\d{2}", text)
    if not year_match:
        return None, 1
    year = int(year_match.group(0))
    month = 1
    month_match = re.search(r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)", text, re.IGNORECASE)
    if month_match:
        month = MONTH_MAP.get(month_match.group(1).lower(), 1)
    return year, month


def _extract_projects(section_text: str) -> list[dict]:
    if not section_text:
        return []
    lines = [l.strip("•- \t") for l in section_text.splitlines() if l.strip()]
    projects = []
    for line in lines[1:8]:  # skip header line
        if 5 < len(line) < 150:
            projects.append({"title": line[:150]})
    return projects


def _extract_certifications(section_text: str) -> list[str]:
    if not section_text:
        return []
    lines = [l.strip("•- \t") for l in section_text.splitlines() if l.strip()]
    return [l[:150] for l in lines[1:8] if 3 < len(l) < 150]


def _extract_job_titles(text: str) -> list[str]:
    titles = set()
    for line in text.splitlines():
        low = line.lower()
        if any(hint in low for hint in JOB_TITLE_HINTS) and len(line.strip()) < 80:
            cleaned = line.strip("•- \t")
            if cleaned:
                titles.add(cleaned)
        if len(titles) >= 8:
            break
    return list(titles)
