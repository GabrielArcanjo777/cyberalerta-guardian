from typing import List


def risk_level_to_pt(level: str) -> str:
    mapping = {
        "low": "baixo",
        "medium": "medio",
        "high": "alto",
        "critical": "critico",
    }
    return mapping.get(level, level)


def build_simple_reply(
    alias: str,
    risk_level_pt: str,
    dangerous_action: str,
    manipulations: List[str],
    trust_lock_recommended: bool,
) -> str:
    text_action = dangerous_action.lower()
    has_financial = any(
        term in manipulations
        for term in ("pedido financeiro", "urgencia", "vinculo familiar", "numero novo")
    )

    if trust_lock_recommended or risk_level_pt in {"alto", "critico"}:
        if text_action == "pix" or "pix" in text_action or has_financial:
            return (
                "Nao faca Pix agora. Essa mensagem tem sinais de golpe. "
                "Estou avisando seu contato de confianca."
            )
        return (
            "Nao siga essa solicitacao agora. Ha sinais de risco. "
            "Estou avisando seu contato de confianca."
        )

    if risk_level_pt == "medio":
        return (
            f"{alias}, espere um instante. Ha sinais de risco nessa mensagem. "
            "Confirme por outro canal antes de agir."
        )

    return (
        f"{alias}, obrigado por compartilhar. Por enquanto nao vejo sinais fortes de golpe, "
        "mas confirme sempre por um canal que voce ja conhece."
    )
