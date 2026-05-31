from app.channels.simple_channel_models import SimpleChannelSubmitRequest


class WhatsAppMockChannel:
    channel_id = "whatsapp_mock"

    def validate(self, payload: SimpleChannelSubmitRequest) -> None:
        if payload.channel != self.channel_id:
            raise ValueError(f"Canal nao suportado: {payload.channel}")
        if payload.content_type != "text":
            raise ValueError("Somente content_type=text no MVP mock.")

    def normalize_content(self, content: str) -> str:
        return content.strip()

    def infer_action_type(self, content: str) -> str:
        lowered = content.lower()
        if any(term in lowered for term in ("pix", "transferencia", "transferir", "pagar", "pagamento")):
            return "pix"
        if "link" in lowered or "http" in lowered:
            return "link"
        if any(term in lowered for term in ("senha", "codigo", "sms")):
            return "codigo"
        return "desconhecido"
