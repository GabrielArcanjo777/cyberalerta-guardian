class ScamClassificationAgent:
    FAMILY_TERMS = {"filho", "filha", "neto", "neta", "irmao", "irma", "mae", "mãe", "pai", "familia", "familiares"}

    def analyze(self, channel: str, action_type: str, message: str) -> str:
        text = message.lower()
        if any(term in text for term in self.FAMILY_TERMS):
            if action_type.lower() in {"pix", "pagamento"}:
                return "falso familiar pedindo Pix"
        if "banco" in text or "link" in text:
            return "falso banco com link"
        if "codigo" in text or "sms" in text:
            return "pedido de codigo SMS"
        if "app remoto" in text or "suporte" in text:
            return "falso suporte com app remoto"
        if "taxa" in text or "emprego" in text:
            return "falso emprego pedindo taxa"
        return "golpe desconhecido"
