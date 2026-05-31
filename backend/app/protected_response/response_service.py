from __future__ import annotations

from typing import List, Optional

from app.protected_response.response_policy import enforce_safe_reply
from app.protected_response.response_schemas import (
    ProtectedResponseGenerateRequest,
    ProtectedResponseGenerateResponse,
)
from app.protected_response.response_templates import (
    TEMPLATES,
    contact_suffix,
    contact_wait,
    or_responsible,
    verify_suffix,
)

HIGH_RISK_LEVELS = {"alto", "critico", "high", "critical"}
MEDIUM_RISK_LEVELS = {"medio", "medium"}


def normalize_risk_level(risk_level: str) -> str:
    normalized = risk_level.strip().lower()
    mapping = {
        "low": "baixo",
        "medium": "medio",
        "high": "alto",
        "critical": "critico",
    }
    return mapping.get(normalized, normalized)


def is_high_risk(risk_level: str) -> bool:
    return normalize_risk_level(risk_level) in HIGH_RISK_LEVELS


def is_medium_risk(risk_level: str) -> bool:
    return normalize_risk_level(risk_level) in MEDIUM_RISK_LEVELS


def infer_category(
    *,
    dangerous_action: str,
    content: str,
    manipulations: Optional[List[str]] = None,
    explicit_category: Optional[str] = None,
) -> str:
    if explicit_category and explicit_category in TEMPLATES:
        return explicit_category

    lowered = content.lower()
    action = dangerous_action.lower()

    if action == "pix" or "pix" in lowered or "transfer" in lowered:
        return "golpe_pix"
    if action == "link" or "http" in lowered or "link" in lowered:
        return "link_suspeito"
    if action == "codigo" or any(term in lowered for term in ("senha", "codigo", "código", "sms")):
        return "codigo_senha"
    if any(term in lowered for term in ("banco", "cadastro", "multa", "fatura")):
        return "falso_banco"
    if manipulations and "pedido financeiro" in manipulations:
        return "golpe_pix"
    return "generico"


def map_manipulations_to_signals(manipulations: List[str]) -> List[str]:
    mapping = {
        "urgencia": "urgencia",
        "numero novo": "numero_novo",
        "pedido financeiro": "pedido_pix",
        "vinculo familiar": "identidade_familiar",
        "pedido para nao ligar": "isolamento",
        "promessa financeira": "pressao_financeira",
    }
    signals: List[str] = []
    for item in manipulations:
        signals.append(mapping.get(item, item.replace(" ", "_")))
    return signals


class ProtectedPersonResponseService:
    def generate(self, request: ProtectedResponseGenerateRequest) -> ProtectedResponseGenerateResponse:
        risk = normalize_risk_level(request.risk_level)
        category = request.category if request.category in TEMPLATES else "generico"
        if risk == "baixo" and category == "generico":
            category = "risco_baixo"

        template = TEMPLATES[category]
        high = is_high_risk(risk)
        medium = is_medium_risk(risk)

        if risk == "baixo":
            body = template.low_risk.format(
                contact_suffix=contact_suffix(request.trusted_contact_alias, False),
                verify_suffix=verify_suffix(request.trusted_contact_alias, False),
                contact_wait=contact_wait(request.trusted_contact_alias),
                or_responsible=or_responsible(request.trusted_contact_alias),
            )
            next_step = template.next_step_low
        elif high:
            body = template.high_risk.format(
                contact_suffix=contact_suffix(request.trusted_contact_alias, True),
                verify_suffix=verify_suffix(request.trusted_contact_alias, True),
                contact_wait=contact_wait(request.trusted_contact_alias),
                or_responsible=or_responsible(request.trusted_contact_alias),
            )
            next_step = template.next_step_high
        elif medium:
            body = template.medium_risk.format(
                contact_suffix=contact_suffix(request.trusted_contact_alias, False),
                verify_suffix=verify_suffix(request.trusted_contact_alias, False),
                contact_wait=contact_wait(request.trusted_contact_alias),
                or_responsible=or_responsible(request.trusted_contact_alias),
            )
            next_step = template.next_step_high
        else:
            body = template.low_risk.format(
                contact_suffix=contact_suffix(request.trusted_contact_alias, False),
                verify_suffix=verify_suffix(request.trusted_contact_alias, False),
                contact_wait=contact_wait(request.trusted_contact_alias),
                or_responsible=or_responsible(request.trusted_contact_alias),
            )
            next_step = template.next_step_low

        short_reply = enforce_safe_reply(body)

        return ProtectedResponseGenerateResponse(
            short_reply=short_reply,
            tone="calm_clear",
            do_not_do=list(template.do_not_do),
            next_step=next_step,
        )
