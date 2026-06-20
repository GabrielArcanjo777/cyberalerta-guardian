from __future__ import annotations

import re
import unicodedata


def strip_accents(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def normalize_text(value: str | None) -> str:
    without_accents = strip_accents(str(value or ""))
    lowered = without_accents.lower()
    collapsed = re.sub(r"\s+", " ", lowered).strip()
    return collapsed


def tokenize_text(value: str | None) -> list[str]:
    return re.findall(r"[a-z0-9]+", normalize_text(value))
