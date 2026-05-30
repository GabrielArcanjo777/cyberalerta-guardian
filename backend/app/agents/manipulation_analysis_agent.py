from typing import List


class ManipulationAnalysisAgent:
    def analyze(self, message: str) -> List[str]:
        text = message.lower()
        manipulations = []
        if any(term in text for term in ["pai", "mae", "filho", "neto", "familia", "primo"]):
            manipulations.append("vinculo familiar")
        if any(term in text for term in ["urgente", "imediato", "agora", "rapido", "reuniao"]):
            manipulations.append("urgencia")
        if "numero novo" in text or "troquei de numero" in text or "celular quebrou" in text:
            manipulations.append("numero novo")
        if any(term in text for term in ["pix", "transferencia", "dinheiro", "pagar"]):
            manipulations.append("pedido financeiro")
        if any(term in text for term in ["nao liga", "nao conte", "so voce", "isolamento"]):
            manipulations.append("pedido para nao ligar")
        if any(term in text for term in ["taxa", "emprego", "ganhar dinheiro"]):
            manipulations.append("promessa financeira")
        if not manipulations:
            manipulations.append("urgencia")
        return manipulations
