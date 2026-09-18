import json
from typing import Any


def to_json(value: Any) -> str:
    """Serialize a Python object to a JSON string for storage in a Text column."""
    return json.dumps(value if value is not None else [], ensure_ascii=False)


def from_json(value: str | None, default: Any = None):
    """Deserialize a JSON string from a Text column back to a Python object."""
    if not value:
        return default if default is not None else []
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return default if default is not None else []
