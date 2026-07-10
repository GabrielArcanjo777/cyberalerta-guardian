class IntentDetectionAgent:
    def analyze(self, action_type: str, message: str) -> str:
        normalized = action_type.lower().strip()
        if normalized in {"pix", "pagamento"}:
            return "pix"
        if "link" in message.lower():
            return "link"
        if "codigo" in message.lower() or "sms" in message.lower():
            return "codigo"
        return normalized or "desconhecido"
