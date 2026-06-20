from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping, Sequence
from typing import Any

_PHONE_DIGIT_RE = re.compile(r"\d")
_SENSITIVE_KEYWORDS = ("secret", "token", "key", "signature", "authorization", "password")
_PHONE_KEYWORDS = ("phone", "telefone", "number", "numero", "whatsapp")
_PHONE_EXACT_KEYS = {"from", "to"}
_MESSAGE_KEYWORDS = ("message", "mensagem", "body", "text", "payload", "raw")


def _short_hash(value: str | None) -> str:
    normalized = str(value or "").strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:10]


def mask_phone(value: str | None) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    digits = "".join(_PHONE_DIGIT_RE.findall(raw))
    if len(digits) < 4:
        return f"[phone:masked sha256:{_short_hash(raw)}]"
    return f"[phone:***{digits[-4:]} sha256:{_short_hash(raw)}]"


def mask_message(value: str | None) -> str:
    raw = re.sub(r"\s+", " ", str(value or "")).strip()
    if not raw:
        return ""
    if len(raw) <= 24:
        return f"[message:{len(raw)} chars sha256:{_short_hash(raw)}]"
    preview = raw[:16].rstrip()
    return f"{preview}... [message:{len(raw)} chars sha256:{_short_hash(raw)}]"


def mask_secret(value: str | None) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    return f"[secret:{len(raw)} chars sha256:{_short_hash(raw)}]"


def mask_value_for_key(key: str, value: Any) -> Any:
    normalized_key = key.lower()
    if any(keyword in normalized_key for keyword in _SENSITIVE_KEYWORDS):
        return mask_secret(str(value) if value is not None else None)
    if normalized_key in _PHONE_EXACT_KEYS or any(keyword in normalized_key for keyword in _PHONE_KEYWORDS):
        return mask_phone(str(value) if value is not None else None)
    if any(keyword in normalized_key for keyword in _MESSAGE_KEYWORDS):
        if isinstance(value, Mapping):
            return mask_mapping(value)
        return mask_message(str(value) if value is not None else None)
    return mask_log_value(value)


def mask_mapping(values: Mapping[str, Any]) -> dict[str, Any]:
    return {str(key): mask_value_for_key(str(key), value) for key, value in values.items()}


def mask_log_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return mask_mapping(value)
    if isinstance(value, str):
        return value
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        return [mask_log_value(item) for item in value]
    return value
