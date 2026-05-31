from fastapi import FastAPI
from app.agents.orchestrator import GuardianOrchestrator
from app.channels.simple_channel_models import (
    SimpleChannelStatusResponse,
    SimpleChannelSubmitRequest,
    SimpleChannelSubmitResponse,
)
from app.channels.simple_channel_service import SimpleChannelService
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.schemas.recovery import RecoveryRequest, RecoveryResponse
from app.schemas.report import ReportRequest, ReportResponse
from app.services.examples import get_example_scenarios
from app.services.safety_policy import SafetyPolicyService

app = FastAPI(title="CyberAlerta Guardian Backend")
orchestrator = GuardianOrchestrator()
simple_channel_service = SimpleChannelService()

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
