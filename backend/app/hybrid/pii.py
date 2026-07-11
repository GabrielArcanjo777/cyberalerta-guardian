from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass
from typing import List

# --- Content hash for auditing (never store raw content) ----------------------

def content_hash(text: str) -> str:
    """Stable SHA-256 hex of the normalized text, for dedupe/audit without
    persisting the message itself."""
    norm = unicodedata.normalize("NFKC", text or "").strip()
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()


# --- PII redaction ------------------------------------------------------------

_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
# Order matters: card/CPF before generic long-number so they win.
_CARD_RE = re.compile(r"\b(?:\d[ -]?){13,19}\b")
_CPF_RE = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
_PHONE_RE = re.compile(r"\+?\d{0,3}[\s-]?\(?\d{2,3}\)?[\s-]?\d{4,5}[\s-]?\d{4}\b")
_CODE_RE = re.compile(r"\b\d{4,8}\b")


@dataclass
class SanitizationResult:
    text: str
    redactions: List[str]
    truncated: bool


def sanitize_for_llm(
    text: str,
    *,
    max_chars: int = 4000,
    redact_pii: bool = True,
) -> SanitizationResult:
    """Prepare untrusted message text for an external LLM call.

    - strips control characters;
    - optionally replaces PII (card, CPF, phone, standalone codes) with tags so
      the *presence* of a signal is kept but the value never leaves;
    - truncates to ``max_chars``.

    The tags (e.g. ``[CARTAO]``) preserve classification context — the model
    still sees "there is a card / a code" without receiving the real digits.
    """
    raw = text or ""
    cleaned = _CONTROL_CHARS.sub(" ", raw)
    redactions: List[str] = []

    if redact_pii:
        def _mark(tag: str):
            def repl(_m):
                if tag not in redactions:
                    redactions.append(tag)
                return f"[{tag}]"
            return repl

        cleaned = _CARD_RE.sub(_mark("CARTAO"), cleaned)
        cleaned = _CPF_RE.sub(_mark("CPF"), cleaned)
        cleaned = _PHONE_RE.sub(_mark("TELEFONE"), cleaned)
        cleaned = _CODE_RE.sub(_mark("CODIGO"), cleaned)

    truncated = len(cleaned) > max_chars
    if truncated:
        cleaned = cleaned[:max_chars]

    return SanitizationResult(text=cleaned.strip(), redactions=redactions, truncated=truncated)


# --- Prompt-injection detection ----------------------------------------------
# These phrases are recorded as a *technical* signal only. They must NOT, by
# themselves, make a message be classified as a scam.

_INJECTION_PATTERNS = [
    re.compile(p, re.IGNORECASE)
    for p in (
        r"ignore (as |todas as |suas )?instru",
        r"ignore (all |the |your )?(previous|prior|above) instructions",
        r"disregard (the |all |previous )?instructions",
        r"esque(ç|c)a (as |suas )?instru",
        r"voc(ê|e) (agora )?(é|e|deve ser) ",
        r"you are now ",
        r"system prompt",
        r"revele? (o |seu )?prompt",
        r"reveal (your |the )?(system )?prompt",
        r"act as ",
        r"aja como ",
    )
]


def detect_prompt_injection(text: str) -> bool:
    """True if the message contains a phrase that tries to hijack the classifier.

    Purely a technical flag: the Policy Engine uses it to force REVIEW, never to
    call something a scam on its own.
    """
    if not text:
        return False
    lowered = unicodedata.normalize("NFKC", text).lower()
    return any(pattern.search(lowered) for pattern in _INJECTION_PATTERNS)
