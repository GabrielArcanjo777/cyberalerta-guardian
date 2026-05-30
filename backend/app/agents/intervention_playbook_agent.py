from app.schemas.analysis import InterventionPlaybook


class InterventionPlaybookAgent:
    def analyze(self, trusted_contact_name: str) -> InterventionPlaybook:
        return InterventionPlaybook(
            immediate_action="Pare agora e nao faca Pix.",
            verification="Confirme a identidade por outro canal.",
            family_escalation=f"{trusted_contact_name} deve ligar para a pessoa imediatamente.",
            recovery_fallback="Se o Pix ja foi feito, ativar Recovery Mode.",
        )
