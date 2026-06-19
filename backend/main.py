import json
from urllib.parse import parse_qsl

from fastapi import FastAPI, HTTPException, Request
from app.agents.orchestrator import GuardianOrchestrator
from app.channels.simple_channel_models import (
    SimpleChannelStatusResponse,
    SimpleChannelSubmitRequest,
    SimpleChannelSubmitResponse,
)
from app.channels.simple_channel_service import SimpleChannelService
from app.protected_response.response_schemas import (
    ProtectedResponseGenerateRequest,
    ProtectedResponseGenerateResponse,
)
from app.guardian_console.admin_case_models import (
    AdminCase,
    AdminCaseFromChannelRequest,
    AdminCaseListResponse,
    AdminCaseStatusUpdateRequest,
    GuardianConsoleStatusResponse,
)
from app.guardian_console.admin_case_service import AdminCaseService
from app.guardian_console import (
    GuardianConsoleRealCaseDetail,
    GuardianConsoleRealCaseListResponse,
    GuardianConsoleRealFlowService,
    GuardianConsoleRealStatusResponse,
)
from app.consent import (
    ConsentAcceptRequest,
    ConsentActivationError,
    ConsentBotActivationRequest,
    ConsentRevokeRequest,
    ConsentScopeUpdateRequest,
    ConsentService,
    ConsentStatusResponse,
)
from app.protected_response.response_service import ProtectedPersonResponseService
from app.trusted_circle.trusted_circle_models import (
    TrustedCircleEscalateRequest,
    TrustedCircleEscalateResponse,
    TrustedCircleEscalationRecord,
    TrustedCircleStatusResponse,
)
from app.trusted_circle.trusted_circle_service import TrustedCircleService
from app.proof_trust.assisted_proof_session import (
    AssistedProofSessionCreateRequest,
    AssistedProofSessionResponse,
    AssistedProofStepUpdateRequest,
    AssistedProofTrustService,
)
from app.mock_whatsapp import (
    MockWhatsAppFixturesResponse,
    MockWhatsAppInboundRequest,
    MockWhatsAppSimulationResponse,
    MockWhatsAppSimulatorService,
    MockWhatsAppStateResponse,
)
from app.channel_adapters import TwilioSignatureContext
from app.dual_bot import (
    DualBotCaseContextResponse,
    DualBotFlowResponse,
    DualBotFlowService,
    DualBotInboundRequest,
    DualBotProviderStatusResponse,
    GuardianFeedbackRequest,
    GuardianFeedbackResponse,
)
from app.evolution_demo import (
    EvolutionDemoHealthResponse,
    EvolutionDemoService,
    EvolutionDemoWebhookResponse,
)
from app.channel_adapters import EvolutionDemoPayloadError
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.schemas.recovery import RecoveryRequest, RecoveryResponse
from app.schemas.report import ReportRequest, ReportResponse
from app.services.examples import get_example_scenarios
from app.services.safety_policy import SafetyPolicyService
from app.twilio_sandbox import (
    TwilioSandboxHealthResponse,
    TwilioSandboxInboundWebhookResponse,
    TwilioSandboxService,
    TwilioSandboxStatusCallbackResponse,
)

app = FastAPI(title="CyberAlerta Guardian Backend")
orchestrator = GuardianOrchestrator()
simple_channel_service = SimpleChannelService()
protected_person_response_service = ProtectedPersonResponseService()
admin_case_service = AdminCaseService()
trusted_circle_service = TrustedCircleService()
assisted_proof_trust_service = AssistedProofTrustService()
mock_whatsapp_service = MockWhatsAppSimulatorService()
twilio_sandbox_service = TwilioSandboxService()
evolution_demo_service = EvolutionDemoService()
dual_bot_service = DualBotFlowService()
consent_service = ConsentService(dual_bot_service.event_model.event_bus)
guardian_console_real_flow_service = GuardianConsoleRealFlowService(dual_bot_service, consent_service)


async def _twilio_payload_from_request(request: Request) -> dict:
    raw_body = await request.body()
    content_type = request.headers.get("content-type", "").lower()
    if "application/json" in content_type and raw_body:
        parsed = json.loads(raw_body.decode("utf-8"))
        return dict(parsed)
    return dict(parse_qsl(raw_body.decode("utf-8"), keep_blank_values=True))


async def _json_payload_from_request(request: Request) -> dict:
    raw_body = await request.body()
    if not raw_body:
        return {}
    return dict(json.loads(raw_body.decode("utf-8")))


def _ensure_twilio_signature(request: Request, payload: dict) -> None:
    context = TwilioSignatureContext(
        url=str(request.url),
        params=payload,
        signature=request.headers.get("X-Twilio-Signature"),
    )
    if not twilio_sandbox_service.adapter.verify_signature(context):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "cyberalerta-guardian-backend",
    }

@app.get("/examples")
def examples():
    return {"examples": get_example_scenarios()}

@app.post("/analyze", response_model=AnalysisResponse)
def analyze(payload: AnalysisRequest):
    SafetyPolicyService().check_text(payload.message)
    return orchestrator.run_analysis(payload)

@app.post("/recovery", response_model=RecoveryResponse)
def recovery(payload: RecoveryRequest):
    SafetyPolicyService().check_text(" ")
    return orchestrator.run_recovery(payload)

@app.post("/report", response_model=ReportResponse)
def report(payload: ReportRequest):
    if payload.analysis is not None:
        SafetyPolicyService().check_text(payload.analysis.user_message)
    return orchestrator.generate_report(payload)


@app.get("/simple-channel/status", response_model=SimpleChannelStatusResponse)
def simple_channel_status():
    return simple_channel_service.get_status()


@app.post("/simple-channel/submit", response_model=SimpleChannelSubmitResponse)
def simple_channel_submit(payload: SimpleChannelSubmitRequest):
    return simple_channel_service.submit(payload)


@app.get("/mock-whatsapp/fixtures", response_model=MockWhatsAppFixturesResponse)
def mock_whatsapp_fixtures():
    return MockWhatsAppFixturesResponse(fixtures=mock_whatsapp_service.list_fixtures())


@app.post("/mock-whatsapp/simulate-inbound", response_model=MockWhatsAppSimulationResponse)
def mock_whatsapp_simulate_inbound(payload: MockWhatsAppInboundRequest):
    return mock_whatsapp_service.simulate_inbound(payload)


@app.get("/mock-whatsapp/simulations", response_model=MockWhatsAppStateResponse)
def mock_whatsapp_simulations():
    simulations = mock_whatsapp_service.list_simulations()
    return MockWhatsAppStateResponse(simulations=simulations, total=len(simulations))


@app.post("/dual-bot/mock/protected-message", response_model=DualBotFlowResponse)
def dual_bot_mock_protected_message(payload: DualBotInboundRequest):
    return dual_bot_service.receive_mock_message(payload)


@app.get("/dual-bot/status", response_model=DualBotProviderStatusResponse)
def dual_bot_status():
    return dual_bot_service.status()


@app.post("/dual-bot/provider/protected-message", response_model=DualBotFlowResponse)
async def dual_bot_provider_protected_message(request: Request):
    payload = await _json_payload_from_request(request)
    return dual_bot_service.receive_provider_message(payload=payload)


@app.get("/dual-bot/cases/{case_id}/context", response_model=DualBotCaseContextResponse)
def dual_bot_case_context(case_id: str):
    try:
        return dual_bot_service.get_case_context(case_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/dual-bot/cases/{case_id}/feedback", response_model=GuardianFeedbackResponse)
def dual_bot_guardian_feedback(case_id: str, payload: GuardianFeedbackRequest):
    try:
        return dual_bot_service.record_guardian_feedback(case_id, payload)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/consent/status", response_model=ConsentStatusResponse)
def consent_status(protected_person_id: str = "demo-protected-person"):
    return consent_service.get_status(protected_person_id)


@app.post("/consent/accept", response_model=ConsentStatusResponse)
def consent_accept(payload: ConsentAcceptRequest):
    return consent_service.accept(payload)


@app.post("/consent/revoke", response_model=ConsentStatusResponse)
def consent_revoke(payload: ConsentRevokeRequest):
    return consent_service.revoke(payload)


@app.post("/consent/bot/activate", response_model=ConsentStatusResponse)
def consent_bot_activate(payload: ConsentBotActivationRequest):
    try:
        return consent_service.activate_bot(payload)
    except ConsentActivationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/consent/bot/deactivate", response_model=ConsentStatusResponse)
def consent_bot_deactivate(payload: ConsentBotActivationRequest):
    return consent_service.deactivate_bot(payload)


@app.post("/consent/scopes", response_model=ConsentStatusResponse)
def consent_scopes(payload: ConsentScopeUpdateRequest):
    return consent_service.update_scopes(payload)


@app.get("/guardian-console/real/status", response_model=GuardianConsoleRealStatusResponse)
def guardian_console_real_status():
    return guardian_console_real_flow_service.get_status()


@app.get("/guardian-console/real/cases", response_model=GuardianConsoleRealCaseListResponse)
def guardian_console_real_cases():
    return guardian_console_real_flow_service.list_cases()


@app.get("/guardian-console/real/cases/{case_id}", response_model=GuardianConsoleRealCaseDetail)
def guardian_console_real_case_detail(case_id: str):
    try:
        return guardian_console_real_flow_service.get_case_detail(case_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/guardian-console/real/cases/{case_id}/feedback", response_model=GuardianFeedbackResponse)
def guardian_console_real_feedback(case_id: str, payload: GuardianFeedbackRequest):
    try:
        return guardian_console_real_flow_service.record_feedback(case_id, payload)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/channels/twilio/whatsapp/health", response_model=TwilioSandboxHealthResponse)
def twilio_whatsapp_health():
    return twilio_sandbox_service.health()


@app.post("/api/channels/twilio/whatsapp/inbound", response_model=TwilioSandboxInboundWebhookResponse)
async def twilio_whatsapp_inbound(request: Request):
    payload = await _twilio_payload_from_request(request)
    _ensure_twilio_signature(request, payload)
    return twilio_sandbox_service.handle_inbound(payload)


@app.post("/api/channels/twilio/whatsapp/status", response_model=TwilioSandboxStatusCallbackResponse)
async def twilio_whatsapp_status(request: Request):
    payload = await _twilio_payload_from_request(request)
    _ensure_twilio_signature(request, payload)
    return twilio_sandbox_service.handle_status_callback(payload)


@app.get("/webhook/evolution/health", response_model=EvolutionDemoHealthResponse)
def evolution_webhook_health():
    return evolution_demo_service.health()


@app.post("/webhook/evolution", response_model=EvolutionDemoWebhookResponse)
async def evolution_webhook(request: Request):
    payload = await _json_payload_from_request(request)
    try:
        return evolution_demo_service.handle_webhook(payload)
    except EvolutionDemoPayloadError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/protected-response/generate", response_model=ProtectedResponseGenerateResponse)
def protected_response_generate(payload: ProtectedResponseGenerateRequest):
    return protected_person_response_service.generate(payload)


@app.get("/guardian-console/status", response_model=GuardianConsoleStatusResponse)
def guardian_console_status():
    return admin_case_service.get_status()


@app.get("/guardian-console/cases", response_model=AdminCaseListResponse)
def guardian_console_cases():
    return admin_case_service.list_cases()


@app.get("/guardian-console/cases/{case_id}", response_model=AdminCase)
def guardian_console_case_detail(case_id: str):
    return admin_case_service.get_case(case_id)


@app.patch("/guardian-console/cases/{case_id}/status", response_model=AdminCase)
def guardian_console_case_status(case_id: str, payload: AdminCaseStatusUpdateRequest):
    return admin_case_service.update_status(case_id, payload)


@app.post("/guardian-console/cases/from-channel", response_model=AdminCase)
def guardian_console_case_from_channel(payload: AdminCaseFromChannelRequest):
    return admin_case_service.create_from_channel(payload)


@app.get("/trusted-circle/status", response_model=TrustedCircleStatusResponse)
def trusted_circle_status():
    return trusted_circle_service.get_status()


@app.post("/trusted-circle/escalate", response_model=TrustedCircleEscalateResponse)
def trusted_circle_escalate(payload: TrustedCircleEscalateRequest):
    return trusted_circle_service.escalate(payload)


@app.get("/trusted-circle/escalations/{escalation_id}", response_model=TrustedCircleEscalationRecord)
def trusted_circle_escalation_detail(escalation_id: str):
    return trusted_circle_service.get_escalation(escalation_id)


@app.post("/proof-trust/assisted-session", response_model=AssistedProofSessionResponse)
def proof_trust_create_assisted_session(payload: AssistedProofSessionCreateRequest):
    return assisted_proof_trust_service.create_session(payload)


@app.get("/proof-trust/assisted-session/{session_id}", response_model=AssistedProofSessionResponse)
def proof_trust_get_assisted_session(session_id: str):
    return assisted_proof_trust_service.get_session(session_id)


@app.post("/proof-trust/assisted-session/{session_id}/step", response_model=AssistedProofSessionResponse)
def proof_trust_update_assisted_step(session_id: str, payload: AssistedProofStepUpdateRequest):
    return assisted_proof_trust_service.update_step(session_id, payload)
