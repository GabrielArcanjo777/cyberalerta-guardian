from app.schemas.analysis import TrustedCircleAlert


class TrustedCircleAgent:
    def analyze(self, risk_score: int, contact_name: str, user_name: str) -> TrustedCircleAlert:
        should_alert = risk_score >= 81
        message = (
            f"{contact_name}, {user_name} recebeu um pedido urgente de Pix de um numero novo dizendo ser familiar. "
            f"Risco critico. Ligue para ela agora antes de qualquer pagamento."
        )
        return TrustedCircleAlert(
            should_alert=should_alert,
            contact_name=contact_name,
            message=message,
        )
