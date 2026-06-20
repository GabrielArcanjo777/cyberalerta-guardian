from pydantic import BaseModel
from typing import List, Optional


class AnalysisRequest(BaseModel):
    user_name: str
    age_group: str
    trusted_contact_name: str
    trusted_contact_relation: str
    action_type: str
    channel: str
    message: str
    already_acted: bool


class AgentDecisionTraceItem(BaseModel):
    agent: str
    decision: str


class TrustEvidence(BaseModel):
    confidence: int
    evidence: List[str]


class TrustLock(BaseModel):
    activated: bool
    title: str
    reason: str
    message: str


class InterventionPlaybook(BaseModel):
    immediate_action: str
    verification: str
    family_escalation: str
    recovery_fallback: str


class TrustedCircleAlert(BaseModel):
    should_alert: bool
    contact_name: str
    message: str


class ReportModel(BaseModel):
    title: str
    summary: str
    agent_decision: str
    recommended_next_step: str


class AnalysisResponse(BaseModel):
    risk_score: int
    risk_level: str
    dangerous_action: str
    scam_type: str
    scam_stage: str
    manipulations: List[str]
    trust_evidence: TrustEvidence
    agent_decision_trace: List[AgentDecisionTraceItem]
    trust_lock: TrustLock
    proof_of_trust: List[str]
    intervention_playbook: InterventionPlaybook
    trusted_circle_alert: TrustedCircleAlert
    user_message: str
    whatsapp_user_message: Optional[str] = None
    whatsapp_trusted_contact_message: Optional[str] = None
    short_explanation: Optional[str] = None
    next_best_action: Optional[str] = None
    report: ReportModel
