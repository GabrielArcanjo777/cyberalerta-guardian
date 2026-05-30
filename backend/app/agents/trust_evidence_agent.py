from app.schemas.analysis import TrustEvidence
from typing import List


class TrustEvidenceAgent:
    def analyze(self, action_type: str, manipulations: List[str]) -> TrustEvidence:
        evidence = [
            "Pedido de Pix" if action_type.lower() == "pix" else "Acao suspeita",
        ]
        evidence.extend([
            "Urgencia emocional" if "urgencia" in manipulations else "Pressao de tempo",
            "Pedido para nao ligar" if "pedido para nao ligar" in manipulations else "Instrucao a evitar contato",
            "Alegacao de parentesco" if "vinculo familiar" in manipulations else "Falha de verificacao de rede",
        ])
        if "numero novo" in manipulations:
            evidence.append("Numero novo ou identidade nao verificada")
        return TrustEvidence(confidence=94, evidence=evidence)
