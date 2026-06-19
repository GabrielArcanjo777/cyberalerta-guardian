from __future__ import annotations

from app.event_model import RiskAssessment


SUPPORTED_LANGUAGES = {"pt", "en"}


PROTECTED_RISK_MESSAGES = {
    "pt": (
        "Recebi sua mensagem. Ela tem sinais de risco. Nao faca pagamento nem clique em links "
        "por enquanto. Vou avisar seu contato de confianca."
    ),
    "en": (
        "I received your message. It has risk signals. Do not pay or click links for now. "
        "I will notify your trusted contact."
    ),
}

PROTECTED_LOW_RISK_MESSAGES = {
    "pt": (
        "Recebi sua mensagem. Se houver pedido de dinheiro, codigo ou pressa, confirme por outro "
        "canal antes de agir."
    ),
    "en": (
        "I received your message. If someone asks for money, a code, or urgency, verify through "
        "another channel first."
    ),
}

RESPONSIBLE_ALERT_TEMPLATES = {
    "pt": (
        "Alerta Guardian: {person} recebeu uma mensagem com sinais de golpe. Risco: {risk}. "
        "Sinais: {signals}. Caso {case_id}. Acesse o caso para revisar."
    ),
    "en": (
        "Guardian Alert: {person} received a message with scam signals. Risk: {risk}. "
        "Signals: {signals}. Case {case_id}. Open the case to review."
    ),
}


RISK_LABELS = {
    "pt": {"low": "baixo", "medium": "medio", "high": "alto"},
    "en": {"low": "low", "medium": "medium", "high": "high"},
}


SIGNAL_LABELS = {
    "urgency": {"pt": "urgencia", "en": "urgency"},
    "pix_or_payment": {"pt": "Pix ou pagamento", "en": "Pix or payment"},
    "new_number": {"pt": "numero novo", "en": "new number"},
    "unknown_link": {"pt": "link suspeito", "en": "suspicious link"},
    "do_not_call": {"pt": "pedido para nao ligar", "en": "request not to call"},
    "secrecy_request": {"pt": "pedido de segredo", "en": "secrecy request"},
    "emotional_pressure": {"pt": "pressao emocional", "en": "emotional pressure"},
    "password_or_code": {"pt": "codigo ou token", "en": "code or token"},
}


def normalize_language(language: str | None) -> str:
    value = (language or "pt").strip().lower()
    return value if value in SUPPORTED_LANGUAGES else "pt"


def protected_reply_for(assessment: RiskAssessment, *, case_created: bool, language: str | None = None) -> str:
    selected_language = normalize_language(language)
    if case_created or assessment.case_threshold_reached:
        return PROTECTED_RISK_MESSAGES[selected_language]
    return PROTECTED_LOW_RISK_MESSAGES[selected_language]


def responsible_alert_for(
    *,
    protected_person_alias: str,
    risk_level: str,
    signals: list[str],
    case_id: str,
    language: str | None = None,
) -> str:
    selected_language = normalize_language(language)
    signal_text = ", ".join(
        SIGNAL_LABELS.get(signal, {}).get(selected_language, signal)
        for signal in signals
    ) if signals else "sem sinais fortes"
    risk_text = RISK_LABELS[selected_language].get(risk_level, risk_level)
    return RESPONSIBLE_ALERT_TEMPLATES[selected_language].format(
        person=protected_person_alias,
        risk=risk_text,
        signals=signal_text,
        case_id=case_id,
    )
