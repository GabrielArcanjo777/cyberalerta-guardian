import re

FORBIDDEN_PATTERNS = [
    r"\bconfront",
    r"\bresponda ao\b",
    r"\breponda ao\b",
    r"\bsua culpa\b",
    r"\bvoce errou\b",
    r"\bvocê errou\b",
    r"(?<!não )(?<!nao )\bmande (?:a )?senha\b",
    r"(?<!não )(?<!nao )\benvie (?:a )?senha\b",
    r"\bjargao\b",
    r"\bjargão\b",
]

MAX_SENTENCES = 2


def count_sentences(text: str) -> int:
    parts = [part.strip() for part in re.split(r"[.!?]+", text) if part.strip()]
    return len(parts) if parts else 1


def contains_forbidden_phrase(text: str) -> bool:
    lowered = text.lower()
    return any(re.search(pattern, lowered) for pattern in FORBIDDEN_PATTERNS)


def trim_to_max_sentences(text: str, max_sentences: int = MAX_SENTENCES) -> str:
    if count_sentences(text) <= max_sentences:
        return text.strip()
    chunks = re.split(r"(?<=[.!?])\s+", text.strip())
    trimmed = " ".join(chunks[:max_sentences]).strip()
    if trimmed and trimmed[-1] not in ".!?":
        trimmed += "."
    return trimmed


def validate_reply(text: str) -> None:
    if not text.strip():
        raise ValueError("Resposta vazia nao permitida.")
    if contains_forbidden_phrase(text):
        raise ValueError("Resposta contem orientacao proibida.")
    if count_sentences(text) > MAX_SENTENCES:
        raise ValueError("Resposta excede o maximo de duas frases.")


def enforce_safe_reply(text: str) -> str:
    cleaned = " ".join(text.split())
    cleaned = trim_to_max_sentences(cleaned, MAX_SENTENCES)
    validate_reply(cleaned)
    return cleaned
