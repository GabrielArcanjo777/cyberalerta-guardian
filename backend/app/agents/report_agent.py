from app.schemas.analysis import AnalysisResponse, ReportModel
from app.schemas.report import ReportRequest, ReportResponse


class ReportAgent:
    def analyze(self, risk_level: str, scam_type: str, should_alert: bool) -> ReportModel:
        title = "Relatorio CyberAlerta Guardian"
        summary = f"Possivel golpe do {scam_type} com pedido urgente de Pix."
        if should_alert:
            agent_decision = "Trust Lock ativado e contato de confianca alertado."
        else:
            agent_decision = "Recomendacao de monitoramento e verificacao adicional."
        recommended_next_step = "Confirmar por ligacao no numero antigo antes de qualquer pagamento."
        return ReportModel(
            title=title,
            summary=summary,
            agent_decision=agent_decision,
            recommended_next_step=recommended_next_step,
        )

    def generate(self, analysis: AnalysisResponse) -> ReportResponse:
        return ReportResponse(report=analysis.report)

    def generate_from_summary(self) -> ReportResponse:
        return ReportResponse(
            report=ReportModel(
                title="Relatorio CyberAlerta Guardian",
                summary="Analise nao fornecida. Nenhuma decisao adicional gerada.",
                agent_decision="Relatorio padrao gerado.",
                recommended_next_step="Forneca um payload de analise para obter relatorio estruturado.",
            )
        )
