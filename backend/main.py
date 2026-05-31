from fastapi import FastAPI
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
from app.protected_response.response_service import ProtectedPersonResponseService
from app.trusted_circle.trusted_circle_models import (
    TrustedCircleEscalateRequest,
    TrustedCircleEscalateResponse,
    TrustedCircleEscalationRecord,
    TrustedCircleStatusResponse,
)
from app.trusted_circle.trusted_circle_service import TrustedCircleService
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.schemas.recovery import RecoveryRequest, RecoveryResponse
from app.schemas.report import ReportRequest, ReportResponse
from app.services.examples import get_example_scenarios
from app.services.safety_policy import SafetyPolicyService

app = FastAPI(title="CyberAlerta Guardian Backend")
orchestrator = GuardianOrchestrator()
simple_channel_service = SimpleChannelService()
protected_person_response_service = ProtectedPersonResponseService()
admin_case_service = AdminCaseService()
trusted_circle_service = TrustedCircleService()

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
