from typing import Dict, List

SCORING_MAP: Dict[str, int] = {
    "pix": 25,
    "pagamento": 25,
    "link suspeito": 15,
    "senha": 30,
    "codigo": 30,
    "documento": 20,
    "app remoto": 30,
    "urgencia": 15,
    "medo": 15,
    "autoridade falsa": 15,
    "vinculo familiar": 20,
    "numero novo": 20,
    "pedido para nao ligar": 15,
    "nao contar": 15,
    "promessa financeira": 15,
    "taxa de emprego": 15,
}


def compute_score(action_type: str, manipulations: List[str], channel: str, already_acted: bool) -> int:
    score = 0
    if action_type in {"pix", "pagamento"}:
        score += SCORING_MAP["pix"]
    if channel == "whatsapp":
        score += 5
    for manipulation in manipulations:
        score += SCORING_MAP.get(manipulation, 0)
    if already_acted:
        score += 10
    return min(score, 100)


def determine_level(score: int) -> str:
    if score <= 30:
        return "low"
    if score <= 60:
        return "medium"
    if score <= 80:
        return "high"
    return "critical"
