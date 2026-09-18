import re

from app.ml.skills_taxonomy import SKILLS_TAXONOMY

# Pre-compile a regex per canonical skill that matches any of its aliases,
# word-boundary aware so "R" doesn't match inside "React".
_COMPILED_PATTERNS: dict[str, re.Pattern] = {}
for canonical, aliases in SKILLS_TAXONOMY.items():
    escaped = [re.escape(a.strip()) for a in aliases if a.strip()]
    pattern = r"(?<![A-Za-z0-9])(" + "|".join(escaped) + r")(?![A-Za-z0-9])"
    _COMPILED_PATTERNS[canonical] = re.compile(pattern, re.IGNORECASE)


def extract_skills(text: str) -> dict[str, int]:
    """
    Scan `text` for known skills from the taxonomy.
    Returns {canonical_skill_name: mention_count} for every skill found at least once.
    """
    if not text:
        return {}
    found: dict[str, int] = {}
    for canonical, pattern in _COMPILED_PATTERNS.items():
        matches = pattern.findall(text)
        if matches:
            found[canonical] = len(matches)
    return found


def extract_free_form_skills(text: str, max_skills: int = 15) -> list[str]:
    """
    Fallback extractor for a 'Skills' section that lists comma/bullet separated
    items not in the taxonomy (e.g. niche tools). Used to supplement, not replace,
    the taxonomy-based extraction.
    """
    section = _find_skills_section(text)
    if not section:
        return []
    # split on common delimiters
    raw_items = re.split(r"[,\n•|/]", section)
    items = []
    for item in raw_items:
        cleaned = item.strip(" -\t")
        if 1 < len(cleaned) <= 40 and not cleaned.lower().startswith(("skill", "technical")):
            items.append(cleaned)
    # de-dup, preserve order
    seen = set()
    result = []
    for item in items:
        key = item.lower()
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result[:max_skills]


def _find_skills_section(text: str) -> str | None:
    match = re.search(
        r"(?:skills|technical skills|core competencies)\s*:?\s*\n?(.+?)(?:\n\s*\n|\Z)",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if match:
        return match.group(1)[:1000]
    return None
