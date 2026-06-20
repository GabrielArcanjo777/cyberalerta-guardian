from __future__ import annotations

from dataclasses import dataclass


def _risk_key(risk_level: str) -> str:
    value = (risk_level or "").strip().lower()
    if value in {"critical", "critico", "critico", "crítico"}:
        return "critical"
    if value in {"high", "alto"}:
        return "high"
    if value in {"medium", "medio", "médio"}:
        return "medium"
    return "low"


def _signals_text(signals: list[str]) -> str:
    clean = [signal.replace("_", " ").strip() for signal in signals if signal.strip()]
    return ", ".join(clean[:4]) if clean else "pedido incomum ou pressa"


@dataclass(frozen=True)
class WhatsAppMessageTemplates:
    whatsapp_user_message: str
    whatsapp_trusted_contact_message: str
    short_explanation: str
    next_best_action: str


def build_whatsapp_message_templates(
    *,
    user_name: str,
    trusted_contact_name: str,
    trusted_contact_relation: str,
    risk_level: str,
    signals: list[str],
    dangerous_action: str,
) -> WhatsAppMessageTemplates:
    risk = _risk_key(risk_level)
    signals_summary = _signals_text(signals)

    if risk == "critical":
        user_message = (
            f"{user_name}, pare agora. Nao faca {dangerous_action}, nao clique em links e nao envie codigos. "
            f"Esta mensagem tem sinais fortes de risco: {signals_summary}. "
            f"Confirme por ligacao usando um numero que voce ja tinha salvo."
        )
        next_best_action = "Parar agora e confirmar por ligacao usando um numero conhecido."
    elif risk == "high":
        user_message = (
            f"{user_name}, nao faca {dangerous_action} por enquanto. "
            f"Esta mensagem tem sinais de risco: {signals_summary}. "
            f"Vou avisar {trusted_contact_name}, seu contato de confianca."
        )
        next_best_action = "Pausar a acao e aguardar o contato de confianca."
    elif risk == "medium":
        user_message = (
            f"{user_name}, pausa por enquanto. Esta mensagem tem alguns sinais de risco. "
            "Nao clique em links nem envie codigo antes de confirmar por outro canal."
        )
        next_best_action = "Confirmar por outro canal antes de agir."
    else:
        user_message = (
            f"{user_name}, recebi sua mensagem. Nao vi sinais fortes, mas confirme antes de agir "
            "se houver pedido de dinheiro, codigo ou link."
        )
        next_best_action = "Conferir com calma antes de qualquer acao sensivel."

    trusted_contact_message = (
        "Alerta CyberAlerta Guardian: "
        f"{user_name} recebeu uma mensagem com sinais de risco. "
        f"Risco: {risk_level}. Sinais: {signals_summary}. "
        f"Ligue para {user_name} usando um numero conhecido antes de qualquer pagamento ou clique."
    )
    short_explanation = f"Sinais avaliados: {signals_summary}. A orientacao e pausar e confirmar por canal confiavel."
    if trusted_contact_relation:
        short_explanation += f" O contato de confianca indicado e {trusted_contact_name} ({trusted_contact_relation})."

    return WhatsAppMessageTemplates(
        whatsapp_user_message=user_message,
        whatsapp_trusted_contact_message=trusted_contact_message,
        short_explanation=short_explanation,
        next_best_action=next_best_action,
    )
