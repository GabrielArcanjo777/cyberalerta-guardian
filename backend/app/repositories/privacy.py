from __future__ import annotations

import hashlib
import re


def stable_hash(value: str | None) -> str:
    normalized = str(value or "").strip().lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def message_preview(message: str | None, *, max_length: int = 120, store_full_message: bool = False) -> str:
    normalized = re.sub(r"\s+", " ", str(message or "")).strip()
    if store_full_message:
        return normalized[:max_length]
    return normalized[:max_length]
