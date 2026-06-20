from app.agents.intent_detection_agent import IntentDetectionAgent
from app.agents.manipulation_analysis_agent import ManipulationAnalysisAgent
from app.agents.scam_stage_agent import ScamStageAgent
from app.agents.scam_classification_agent import ScamClassificationAgent
from app.agents.risk_scoring_agent import RiskScoringAgent
from app.agents.trust_evidence_agent import TrustEvidenceAgent
from app.agents.trust_lock_agent import TrustLockAgent
from app.agents.proof_of_trust_agent import ProofOfTrustAgent
from app.agents.intervention_playbook_agent import InterventionPlaybookAgent
from app.agents.trusted_circle_agent import TrustedCircleAgent
from app.agents.report_agent import ReportAgent
from app.agents.recovery_agent import RecoveryAgent
from app.services.safety_policy import SafetyPolicyService
from app.services.whatsapp_templates import build_whatsapp_message_templates
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.schemas.recovery import RecoveryRequest, RecoveryResponse
from app.schemas.report import ReportRequest, ReportResponse


class GuardianOrchestrator:
    def __init__(self) -> None:
        self.intent_agent = IntentDetectionAgent()
        self.manipulation_agent = ManipulationAnalysisAgent()
        self.scam_stage_agent = ScamStageAgent()
        self.scam_classification_agent = ScamClassificationAgent()
        self.risk_scoring_agent = RiskScoringAgent()
        self.trust_evidence_agent = TrustEvidenceAgent()
        self.trust_lock_agent = TrustLockAgent()
        self.proof_of_trust_agent = ProofOfTrustAgent()
        self.intervention_playbook_agent = InterventionPlaybookAgent()
        self.trusted_circle_agent = TrustedCircleAgent()
        self.report_agent = ReportAgent()
        self.recovery_agent = RecoveryAgent()
        self.policy_service = SafetyPolicyService()

    def run_analysis(self, request: AnalysisRequest) -> AnalysisResponse:
        self.policy_service.check_text(request.message)

        dangerous_action = self.intent_agent.analyze(request.action_type, request.message)
        manipulations = self.manipulation_agent.analyze(request.message)
        scam_stage = self.scam_stage_agent.analyze(request.already_acted, request.action_type)
        scam_type = self.scam_classification_agent.analyze(request.channel, request.action_type, request.message)
        risk_score = self.risk_scoring_agent.analyze(request.action_type, manipulations, request.channel, request.already_acted)
        risk_level = self.risk_scoring_agent.determine_level(risk_score)
        trust_evidence = self.trust_evidence_agent.analyze(request.action_type, manipulations)
        trust_lock = self.trust_lock_agent.analyze(risk_score, scam_type)
        proof_of_trust = self.proof_of_trust_agent.analyze(request.action_type)
        intervention_playbook = self.intervention_playbook_agent.analyze(request.trusted_contact_name)
        trusted_circle_alert = self.trusted_circle_agent.analyze(risk_score, request.trusted_contact_name, request.user_name)
        report = self.report_agent.analyze(risk_level, scam_type, trusted_circle_alert.should_alert)
        whatsapp_templates = build_whatsapp_message_templates(
            user_name=request.user_name,
            trusted_contact_name=request.trusted_contact_name,
            trusted_contact_relation=request.trusted_contact_relation,
            risk_level=risk_level,
            signals=manipulations,
            dangerous_action=dangerous_action,
        )

        user_message = (
            f"{request.user_name}, pare agora. Nao faca {dangerous_action}. "
            f"Ligue para o numero antigo do seu {request.trusted_contact_relation}."
        )

        return AnalysisResponse(
            risk_score=risk_score,
            risk_level=risk_level,
            dangerous_action=dangerous_action,
            scam_type=scam_type,
            scam_stage=scam_stage,
            manipulations=manipulations,
            trust_evidence=trust_evidence,
            agent_decision_trace=self._build_decision_trace(dangerous_action, manipulations, risk_score),
            trust_lock=trust_lock,
            proof_of_trust=proof_of_trust,
            intervention_playbook=intervention_playbook,
            trusted_circle_alert=trusted_circle_alert,
            user_message=user_message,
            whatsapp_user_message=whatsapp_templates.whatsapp_user_message,
            whatsapp_trusted_contact_message=whatsapp_templates.whatsapp_trusted_contact_message,
            short_explanation=whatsapp_templates.short_explanation,
            next_best_action=whatsapp_templates.next_best_action,
            report=report,
        )

    def _build_decision_trace(self, dangerous_action: str, manipulations: list[str], risk_score: int) -> list[dict]:
        decisions = [
            {"agent": "IntentDetectionAgent", "decision": f"Acao perigosa detectada: {dangerous_action}"},
            {"agent": "ManipulationAnalysisAgent", "decision": f"Manipulacoes detectadas: {', '.join(manipulations)}"},
            {"agent": "RiskScoringAgent", "decision": "Risco critico calculado" if risk_score >= 81 else "Risco calculado"},
            {"agent": "TrustLockAgent", "decision": "Trust Lock ativado" if risk_score >= 81 else "Trust Lock nao ativado"},
            {"agent": "TrustedCircleAgent", "decision": "Alerta familiar recomendado" if risk_score >= 81 else "Alerta familiar opcional"},
        ]
        return decisions

    def run_recovery(self, request: RecoveryRequest) -> RecoveryResponse:
        self.policy_service.check_text(" ")
        return self.recovery_agent.analyze(request)

    def generate_report(self, request: ReportRequest) -> ReportResponse:
        if request.analysis is not None:
            return self.report_agent.generate(request.analysis)
        return self.report_agent.generate_from_summary()
