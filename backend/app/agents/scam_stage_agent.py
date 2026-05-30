class ScamStageAgent:
    def analyze(self, already_acted: bool, action_type: str) -> str:
        if already_acted:
            return "consequencia ja iniciada"
        if action_type.lower() in {"pix", "pagamento"}:
            return "acao perigosa iminente"
        return "fase inicial"
