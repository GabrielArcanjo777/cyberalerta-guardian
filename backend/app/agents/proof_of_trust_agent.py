from typing import List


class ProofOfTrustAgent:
    def analyze(self, action_type: str) -> List[str]:
        proof = [
            "Nao responda o numero novo.",
            "Ligue para o numero antigo da pessoa.",
            "Confirme por chamada de voz.",
            "Nao faca Pix ate confirmar por outro canal.",
        ]
        if action_type.lower() != "pix":
            proof.append("Verifique a origem da solicitacao antes de agir.")
        return proof
