from app.schemas.analysis import TrustLock


class TrustLockAgent:
    def analyze(self, risk_score: int, scam_type: str) -> TrustLock:
        activated = risk_score >= 81
        if activated:
            reason = "Pedido urgente de Pix vindo de numero nao verificado se passando por familiar."
            message = "Essa acao esta em quarentena ate confirmacao por outro canal."
        else:
            reason = "Risco moderado ou baixo detectado."
            message = "Monitore e confirme antes de prosseguir."
        return TrustLock(
            activated=activated,
            title="TRUST LOCK ATIVADO" if activated else "TRUST LOCK DESATIVADO",
            reason=reason,
            message=message,
        )
