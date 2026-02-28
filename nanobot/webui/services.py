"""Reusable WebUI service helpers."""

from __future__ import annotations

def safe_positive_int(raw: str | None, *, default: int = 1, minimum: int = 1) -> int:
    try:
        value = int((raw or "").strip())
    except Exception:
        return default
    return value if value >= minimum else default
