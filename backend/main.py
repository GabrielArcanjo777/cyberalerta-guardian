import hmac
import json
import logging
import re
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.agents.orchestrator import GuardianOrchestrator
from app.channels.simple_channel_models import (
    SimpleChannelStatusResponse,
    SimpleChannelSubmitRequest,
    SimpleChannelSubmitResponse,
)
from app.channels.simple_channel_service import SimpleChannelService
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
from app.event_model import EventModelService
from app.core.config import config
from app.storage import settings_store
from app.hybrid.query import get_hybrid_decision_for_case
from app.core.middleware import RequestContextHeadersMiddleware, SecurityHeadersMiddleware
from app.core.security import check_rate_limit, require_api_key, validate_message_text
from app.auth import create_auth_router, require_sensitive_access
from app.integrations.n8n import N8nIntegrationService, create_n8n_router
from app.integrations.evolution import create_evolution_router

logger = logging.getLogger("uvicorn.error")

app = FastAPI(title="CyberAlerta Guardian Backend", debug=False)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestContextHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
orchestrator = GuardianOrchestrator()
simple_channel_service = SimpleChannelService()
admin_case_service = AdminCaseService()
trusted_circle_service = TrustedCircleService()
assisted_proof_trust_service = AssistedProofTrustService()
# Single shared Event Model (SQLite or in-memory per STORAGE_BACKEND) so every
# channel writes to one persisted store and the Guardian Console sees all cases.
event_model = EventModelService.from_config()
mock_whatsapp_service = MockWhatsAppSimulatorService(event_model=event_model)
evolution_demo_service = EvolutionDemoService(event_model=event_model)
dual_bot_service = DualBotFlowService(event_model=event_model)
consent_service = ConsentService(dual_bot_service.event_model.event_bus)
guardian_console_real_flow_service = GuardianConsoleRealFlowService(dual_bot_service, consent_service)
n8n_integration_service = N8nIntegrationService(orchestrator=orchestrator)

def _apply_runtime_safety(*, dry_run: bool | None = None, real_send: bool | None = None) -> None:
    """Apply safety-gate toggles at runtime (UI-driven, no .env edit).

    The gate lives in the frozen EvolutionDemoConfig on the adapter, so we swap
    it via dataclasses.replace. The allowlist is always re-synced to the single
    TRUSTED_CONTACT — the only recipient the bot may ever message — so enabling
    real send never opens delivery to anyone else.
    """
    import dataclasses

    if dry_run is not None:
        config.dry_run = dry_run
    if real_send is not None:
        config.beta_real_send_enabled = real_send
    updates: dict = {
        "dry_run": config.dry_run,
        "real_send_enabled": config.beta_real_send_enabled,
    }
    if config.trusted_contact:
        updates["allowed_recipients"] = (config.trusted_contact,)
    new_cfg = dataclasses.replace(evolution_demo_service.adapter.config, **updates)
    evolution_demo_service.adapter.config = new_cfg
    evolution_demo_service.config = new_cfg


_persisted_tc = settings_store.get("trusted_contact")
if _persisted_tc is not None and not config.trusted_contact:
    config.trusted_contact = _persisted_tc
    evolution_demo_service.guardian_address = _persisted_tc or None
    dual_bot_service.default_guardian_address = _persisted_tc or "+5511888880001"

_persisted_protected = settings_store.get("protected_number")
if _persisted_protected is not None and not config.protected_number:
    config.protected_number = _persisted_protected

# Safety toggles configured via UI survive restarts (stored values win over .env,
# since the console is the operator surface).
_persisted_dry = settings_store.get("dry_run")
_persisted_real = settings_store.get("beta_real_send_enabled")
_apply_runtime_safety(
    dry_run=(_persisted_dry == "true") if _persisted_dry is not None else None,
    real_send=(_persisted_real == "true") if _persisted_real is not None else None,
)

app.include_router(create_auth_router())
app.include_router(create_n8n_router(n8n_integration_service))
app.include_router(create_evolution_router(), prefix="/api/channels/evolution")


async def _json_payload_from_request(request: Request) -> dict:
    raw_body = await request.body()
    if not raw_body:
        return {}
    return dict(json.loads(raw_body.decode("utf-8")))


def _validate_analysis_payload(payload: AnalysisRequest) -> None:
    payload.message = validate_message_text(payload.message, field_name="message")


def _validate_evolution_webhook_secret(request: Request) -> None:
    if not config.evolution_webhook_secret:
        # Same policy as the n8n webhook: tolerated only in development; in
        # production an unset secret must never leave the endpoint open.
        if config.is_development:
            logger.warning("Evolution webhook accepted without secret (development only).")
            return None
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error",
        )

    header = request.headers.get("X-Evolution-Webhook-Secret")
    if not header or not hmac.compare_digest(header, config.evolution_webhook_secret):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception while processing request")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


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
def analyze(request: Request, payload: AnalysisRequest):
    check_rate_limit(request, bucket="analyze")
    _validate_analysis_payload(payload)
    SafetyPolicyService().check_text(payload.message)
    return orchestrator.run_analysis(payload)

@app.post("/recovery", response_model=RecoveryResponse)
def recovery(request: Request, payload: RecoveryRequest):
    check_rate_limit(request, bucket="recovery")
    SafetyPolicyService().check_text(" ")
    return orchestrator.run_recovery(payload)

@app.post("/report", response_model=ReportResponse)
def report(request: Request, payload: ReportRequest):
    check_rate_limit(request, bucket="report")
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
async def dual_bot_provider_protected_message(request: Request, api_key: None = Depends(require_api_key)):
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
def consent_status(protected_person_id: str = "demo-protected-person", access: None = Depends(require_sensitive_access)):
    return consent_service.get_status(protected_person_id)


@app.post("/consent/accept", response_model=ConsentStatusResponse)
def consent_accept(payload: ConsentAcceptRequest, access: None = Depends(require_sensitive_access)):
    return consent_service.accept(payload)


@app.post("/consent/revoke", response_model=ConsentStatusResponse)
def consent_revoke(payload: ConsentRevokeRequest, access: None = Depends(require_sensitive_access)):
    return consent_service.revoke(payload)


@app.post("/consent/bot/activate", response_model=ConsentStatusResponse)
def consent_bot_activate(payload: ConsentBotActivationRequest, access: None = Depends(require_sensitive_access)):
    try:
        return consent_service.activate_bot(payload)
    except ConsentActivationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/consent/bot/deactivate", response_model=ConsentStatusResponse)
def consent_bot_deactivate(payload: ConsentBotActivationRequest, access: None = Depends(require_sensitive_access)):
    return consent_service.deactivate_bot(payload)


@app.post("/consent/scopes", response_model=ConsentStatusResponse)
def consent_scopes(payload: ConsentScopeUpdateRequest, access: None = Depends(require_sensitive_access)):
    return consent_service.update_scopes(payload)


@app.get("/guardian-console/real/status", response_model=GuardianConsoleRealStatusResponse)
def guardian_console_real_status(access: None = Depends(require_sensitive_access)):
    return guardian_console_real_flow_service.get_status()


@app.get("/guardian-console/real/cases", response_model=GuardianConsoleRealCaseListResponse)
def guardian_console_real_cases(access: None = Depends(require_sensitive_access)):
    return guardian_console_real_flow_service.list_cases()


@app.get("/guardian-console/real/cases/{case_id}", response_model=GuardianConsoleRealCaseDetail)
def guardian_console_real_case_detail(case_id: str, access: None = Depends(require_sensitive_access)):
    try:
        return guardian_console_real_flow_service.get_case_detail(case_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/guardian-console/real/cases/{case_id}/hybrid-decision")
def guardian_console_hybrid_decision(case_id: str, access: None = Depends(require_sensitive_access)):
    """Latest hybrid decision (deterministic + LLM + Policy) for a case, or
    {available: false} when the pipeline produced none for it."""
    decision = get_hybrid_decision_for_case(event_model, case_id)
    if decision is None:
        return {"available": False}
    return {"available": True, "decision": decision}


@app.post("/guardian-console/real/cases/{case_id}/feedback", response_model=GuardianFeedbackResponse)
def guardian_console_real_feedback(case_id: str, payload: GuardianFeedbackRequest, access: None = Depends(require_sensitive_access)):
    try:
        return guardian_console_real_flow_service.record_feedback(case_id, payload)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/webhook/evolution/health", response_model=EvolutionDemoHealthResponse)
def evolution_webhook_health():
    return evolution_demo_service.health()


@app.post("/webhook/evolution", response_model=EvolutionDemoWebhookResponse)
async def evolution_webhook(request: Request):
    # Reject unauthorized callers before reading/parsing the (untrusted) body.
    _validate_evolution_webhook_secret(request)
    check_rate_limit(request, bucket="evolution_webhook")
    payload = await _json_payload_from_request(request)
    try:
        return evolution_demo_service.handle_webhook(payload)
    except EvolutionDemoPayloadError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


_PHONE_DIGITS_RE = re.compile(r"^\+?\d{10,15}$")


def _protection_settings() -> dict:
    return {
        "protected_number": config.protected_number,
        "trusted_contact": config.trusted_contact,
        "dry_run": config.dry_run,
        "beta_real_send_enabled": config.beta_real_send_enabled,
    }


@app.get("/settings/trusted-contact")
def settings_get_trusted_contact(access: None = Depends(require_sensitive_access)):
    return _protection_settings()


@app.put("/settings/trusted-contact")
def settings_set_trusted_contact(request: Request, payload: dict, access: None = Depends(require_sensitive_access)):
    # Both fields are optional per request; only validate the ones present. The
    # bot never messages the protected number — it is stored for identification.
    if "trusted_contact" in payload:
        number = (payload.get("trusted_contact") or "").strip()
        if number and not _PHONE_DIGITS_RE.match(number):
            raise HTTPException(status_code=422, detail="Contato de confianca invalido. Use +DDI seguido de 10-15 digitos.")
        config.trusted_contact = number
        evolution_demo_service.guardian_address = number or None
        dual_bot_service.default_guardian_address = number or "+5511888880001"
        settings_store.put("trusted_contact", number)

    if "protected_number" in payload:
        protected = (payload.get("protected_number") or "").strip()
        if protected and not _PHONE_DIGITS_RE.match(protected):
            raise HTTPException(status_code=422, detail="Numero da pessoa protegida invalido. Use +DDI seguido de 10-15 digitos.")
        config.protected_number = protected
        settings_store.put("protected_number", protected)

    # Safety-gate toggles (UI switches instead of .env edits). Strict booleans
    # only; the allowlist stays pinned to TRUSTED_CONTACT inside the helper.
    dry_run_value: bool | None = None
    real_send_value: bool | None = None
    if "dry_run" in payload:
        if not isinstance(payload["dry_run"], bool):
            raise HTTPException(status_code=422, detail="dry_run deve ser booleano.")
        dry_run_value = payload["dry_run"]
        settings_store.put("dry_run", "true" if dry_run_value else "false")
    if "beta_real_send_enabled" in payload:
        if not isinstance(payload["beta_real_send_enabled"], bool):
            raise HTTPException(status_code=422, detail="beta_real_send_enabled deve ser booleano.")
        real_send_value = payload["beta_real_send_enabled"]
        settings_store.put("beta_real_send_enabled", "true" if real_send_value else "false")
    if dry_run_value is not None or real_send_value is not None or "trusted_contact" in payload:
        _apply_runtime_safety(dry_run=dry_run_value, real_send=real_send_value)

    return _protection_settings()


@app.get("/guardian-console/status", response_model=GuardianConsoleStatusResponse)
def guardian_console_status(access: None = Depends(require_sensitive_access)):
    return admin_case_service.get_status()


@app.get("/guardian-console/cases", response_model=AdminCaseListResponse)
def guardian_console_cases(access: None = Depends(require_sensitive_access)):
    return admin_case_service.list_cases()


@app.get("/guardian-console/cases/{case_id}", response_model=AdminCase)
def guardian_console_case_detail(case_id: str, access: None = Depends(require_sensitive_access)):
    return admin_case_service.get_case(case_id)


@app.patch("/guardian-console/cases/{case_id}/status", response_model=AdminCase)
def guardian_console_case_status(case_id: str, payload: AdminCaseStatusUpdateRequest, access: None = Depends(require_sensitive_access)):
    return admin_case_service.update_status(case_id, payload)


@app.post("/guardian-console/cases/from-channel", response_model=AdminCase)
def guardian_console_case_from_channel(payload: AdminCaseFromChannelRequest, access: None = Depends(require_sensitive_access)):
    return admin_case_service.create_from_channel(payload)


@app.get("/trusted-circle/status", response_model=TrustedCircleStatusResponse)
def trusted_circle_status(access: None = Depends(require_sensitive_access)):
    return trusted_circle_service.get_status()


@app.post("/trusted-circle/escalate", response_model=TrustedCircleEscalateResponse)
def trusted_circle_escalate(payload: TrustedCircleEscalateRequest, access: None = Depends(require_sensitive_access)):
    return trusted_circle_service.escalate(payload)


@app.get("/trusted-circle/escalations/{escalation_id}", response_model=TrustedCircleEscalationRecord)
def trusted_circle_escalation_detail(escalation_id: str, access: None = Depends(require_sensitive_access)):
    return trusted_circle_service.get_escalation(escalation_id)


@app.post("/proof-trust/assisted-session", response_model=AssistedProofSessionResponse)
def proof_trust_create_assisted_session(payload: AssistedProofSessionCreateRequest, access: None = Depends(require_sensitive_access)):
    return assisted_proof_trust_service.create_session(payload)


@app.get("/proof-trust/assisted-session/{session_id}", response_model=AssistedProofSessionResponse)
def proof_trust_get_assisted_session(session_id: str, access: None = Depends(require_sensitive_access)):
    return assisted_proof_trust_service.get_session(session_id)


@app.post("/proof-trust/assisted-session/{session_id}/step", response_model=AssistedProofSessionResponse)
def proof_trust_update_assisted_step(session_id: str, payload: AssistedProofStepUpdateRequest, access: None = Depends(require_sensitive_access)):
    return assisted_proof_trust_service.update_step(session_id, payload)
