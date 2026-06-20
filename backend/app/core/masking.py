import re


def mask_phone(value: str | None) -> str:
    if not value:
        return "unknown"
    cleaned = re.sub(r"[^0-9+]", "", value)
    if len(cleaned) <= 4:
        return "***"
    return cleaned[:3] + "****" + cleaned[-2:]


def mask_secret(value: str | None) -> str:
    if not value:
        return ""
    if len(value) <= 4:
        return "***"
    return value[:2] + "***" + value[-2:]


def mask_message(value: str | None, *, max_length: int = 60) -> str:
    if not value:
        return ""
    text = value.strip()
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."
