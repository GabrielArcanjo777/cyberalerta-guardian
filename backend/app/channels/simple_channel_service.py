from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4

from fastapi import HTTPException

from app.agents.intent_detection_agent import IntentDetectionAgent
from app.agents.manipulation_analysis_agent import ManipulationAnalysisAgent
from app.agents.risk_scoring_agent import RiskScoringAgent
from app.channels.protected_person_response import risk_level_to_pt
from app.channels.simple_channel_models import (
    SimpleChannelStatusResponse,
    SimpleChannelSubmitRequest,
    SimpleChannelSubmitResponse,
)
from app.channels.whatsapp_mock_channel import WhatsAppMockChannel
from app.protected_response.response_schemas import ProtectedResponseGenerateRequest
from app.protected_response.response_service import (
    ProtectedPersonResponseService,
    infer_category,
    map_manipulations_to_signals,
)
from app.services.safety_policy import SafetyPolicyService

_CASE_STORE: Dict[str, Dict[str, Any]] = {}


class SimpleChannelService:
    def __init__(self) -> None:
        self.policy = SafetyPolicyService()
        self.whatsapp_mock = WhatsAppMockChannel()
        self.intent_agent = IntentDetectionAgent()
        self.manipulation_agent = ManipulationAnalysisAgent()
        self.risk_agent = RiskScoringAgent()
        self.protected_response = ProtectedPersonResponseService()

    def get_status(self) -> SimpleChannelStatusResponse:
        return SimpleChannelStatusResponse(
            service="simple-channel-intake",
            mode="whatsapp_mock",
            channels=[self.whatsapp_mock.channel_id],
            whatsapp_real_enabled=False,
            monitoring_enabled=False,
            privacy_note=(
                "Entrada voluntaria com consentimento. Nenhuma conversa privada e monitorada. "
                "Dados minimizados para demonstracao."
            ),
            demo_note=(
                "WhatsApp real e integracao futura. Este MVP usa conversa simulada sem tokens ou envio real."
            ),
        )

    def submit(self, payload: SimpleChannelSubmitRequest) -> SimpleChannelSubmitResponse:
        if not payload.consent:
            raise HTTPException(
                status_code=400,
                detail="Consentimento explicito e obrigatorio para enviar conteudo ao Guardian.",
            )

        self.whatsapp_mock.validate(payload)
        content = self.whatsapp_mock.normalize_content(payload.content)
        self.policy.check_text(content)

        action_type = self.whatsapp_mock.infer_action_type(content)
        dangerous_action = self.intent_agent.analyze(action_type, content)
        manipulations = self.manipulation_agent.analyze(content)
        risk_score = self.risk_agent.analyze(action_type, manipulations, "whatsapp", False)
        risk_level = self.risk_agent.determine_level(risk_score)
        risk_level_pt = risk_level_to_pt(risk_level)
        trust_lock_recommended = risk_score >= 81
        admin_case_created = payload.consent and risk_score >= 41

        category = infer_category(
            dangerous_action=dangerous_action,
            content=content,
            manipulations=manipulations,
        )
        signals = map_manipulations_to_signals(manipulations)

        protected = self.protected_response.generate(
            ProtectedResponseGenerateRequest(
                risk_level=risk_level_pt,
                category=category,
                signals=signals,
                trusted_contact_alias=payload.trusted_contact_alias,
            )
        )
        simple_reply = protected.short_reply

        case_id = f"ch-{uuid4().hex[:12]}"
        _CASE_STORE[case_id] = {
            "channel_case_id": case_id,
            "protected_person_alias": payload.protected_person_alias,
            "channel": payload.channel,
            "content_type": payload.content_type,
            "content": content,
            "risk_score": risk_score,
            "risk_level": risk_level_pt,
            "dangerous_action": dangerous_action,
            "manipulations": manipulations,
            "category": category,
            "signals": signals,
            "protected_response": protected.model_dump(),
            "admin_case_created": admin_case_created,
            "trust_lock_recommended": trust_lock_recommended,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        return SimpleChannelSubmitResponse(
            channel_case_id=case_id,
            risk_level=risk_level_pt,
            simple_reply=simple_reply,
            admin_case_created=admin_case_created,
            trust_lock_recommended=trust_lock_recommended,
        )

    def list_cases(self) -> Dict[str, Dict[str, Any]]:
        return dict(_CASE_STORE)
