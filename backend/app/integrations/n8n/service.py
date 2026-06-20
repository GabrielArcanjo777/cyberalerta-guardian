from __future__ import annotations

import logging

from app.agents.orchestrator import GuardianOrchestrator
from app.core.config import config
from app.core.logging import get_logger, structured_log
from app.core.security import validate_message_text
from app.repositories import (
    AuditEventRecord,
    CaseProcessingStatus,
    InboundMessageRecord,
    InboundProcessingStatus,
    StateCase,
    get_operational_state_repository,
    message_preview,
    stable_hash,
)
from app.repositories.base import OperationalStateRepository
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.services.text_normalization import normalize_text

from .schemas import N8nHealthResponse, N8nWhatsAppInboundRequest, N8nWhatsAppInboundResponse

logger = get_logger("n8n")


class N8nMessageAlreadyProcessingError(Exception):
    """Raised when n8n retries an inbound message while the first attempt is still running."""


class N8nIntegrationService:
    def __init__(
        self,
        *,
        orchestrator: GuardianOrchestrator,
        state_repository: OperationalStateRepository | None = None,
    ) -> None:
        self._orchestrator = orchestrator
        self._state = state_repository or get_operational_state_repository()

    def health(self) -> N8nHealthResponse:
        return N8nHealthResponse(
            dry_run=config.dry_run,
            auth_header=config.n8n_webhook_header,
            production=config.is_production,
        )

    def handle_whatsapp_inbound(
        self,
        payload: N8nWhatsAppInboundRequest,
        *,
        request_id: str | None,
        n8n_execution_id: str | None,
    ) -> N8nWhatsAppInboundResponse:
        message_id = self._message_id(payload)
        structured_log(
            logger,
            "n8n_inbound_received",
            request_id=request_id,
            n8n_execution_id=n8n_execution_id,
            message_id=message_id,
            channel=payload.channel,
            from_number=payload.from_number,
            message=payload.message,
        )
        inbound_record, reserved = self._reserve_inbound(payload, message_id, n8n_execution_id)
        if (
            not reserved
            and inbound_record.processing_status == InboundProcessingStatus.PROCESSED
            and inbound_record.last_response_json is not None
        ):
            self._state.audit_events.append(
                AuditEventRecord(
                    case_id=inbound_record.case_id,
                    request_id=request_id,
                    n8n_execution_id=n8n_execution_id,
                    event_type="duplicate_message_ignored",
                    metadata={"message_id": message_id, "channel": payload.channel},
                )
            )
            structured_log(
                logger,
                "duplicate_message_ignored",
                request_id=request_id,
                n8n_execution_id=n8n_execution_id,
                message_id=message_id,
                case_id=inbound_record.case_id,
                channel=payload.channel,
            )
            return N8nWhatsAppInboundResponse.model_validate(inbound_record.last_response_json)

        if not reserved:
            self._state.audit_events.append(
                AuditEventRecord(
                    case_id=inbound_record.case_id,
                    request_id=request_id,
                    n8n_execution_id=n8n_execution_id,
                    event_type="duplicate_message_still_processing",
                    metadata={"message_id": message_id, "channel": payload.channel},
                )
            )
            structured_log(
                logger,
                "duplicate_message_still_processing",
                level=logging.WARNING,
                request_id=request_id,
                n8n_execution_id=n8n_execution_id,
                message_id=message_id,
                case_id=inbound_record.case_id,
                channel=payload.channel,
            )
            raise N8nMessageAlreadyProcessingError(message_id)

        if (
            inbound_record.processing_status == InboundProcessingStatus.PROCESSED
            and inbound_record.last_response_json is not None
        ):
            self._state.audit_events.append(
                AuditEventRecord(
                    case_id=inbound_record.case_id,
                    request_id=request_id,
                    n8n_execution_id=n8n_execution_id,
                    event_type="duplicate_message_ignored",
                    metadata={"message_id": message_id, "channel": payload.channel},
                )
            )
            structured_log(
                logger,
                "duplicate_message_ignored",
                request_id=request_id,
                n8n_execution_id=n8n_execution_id,
                message_id=message_id,
                case_id=inbound_record.case_id,
                channel=payload.channel,
            )
            return N8nWhatsAppInboundResponse.model_validate(inbound_record.last_response_json)

        analysis_request = self._analysis_request(payload)
        analysis = self._orchestrator.run_analysis(analysis_request)
        case_id = f"n8n-case-{stable_hash(message_id)[:16]}"
        response = self._response_from_analysis(
            analysis,
            payload=payload,
            case_id=case_id,
            request_id=request_id,
            n8n_execution_id=n8n_execution_id,
        )
        self._save_state(
            payload=payload,
            inbound_record=inbound_record,
            response=response,
            request_id=request_id,
            n8n_execution_id=n8n_execution_id,
        )
        structured_log(
            logger,
            "n8n_response_prepared",
            request_id=request_id,
            n8n_execution_id=n8n_execution_id,
            case_id=response.case_id,
            message_id=message_id,
            risk_score=response.risk_score,
            risk_level=response.risk_level,
            n8n_action=response.n8n_action,
            dry_run=response.dry_run,
        )
        return response

    def _analysis_request(self, payload: N8nWhatsAppInboundRequest) -> AnalysisRequest:
        message = validate_message_text(payload.message, field_name="body")
        return AnalysisRequest(
            user_name=payload.user_name or "Pessoa protegida",
            age_group="adult",
            trusted_contact_name=payload.trusted_contact_name or "Contato de confianca",
            trusted_contact_relation=payload.trusted_contact_relation or "contato de confianca",
            action_type=payload.action_type or self._infer_action_type(payload.message),
            channel=payload.channel,
            message=message,
            already_acted=payload.already_acted,
        )

    def _response_from_analysis(
        self,
        analysis: AnalysisResponse,
        *,
        payload: N8nWhatsAppInboundRequest,
        case_id: str,
        request_id: str | None,
        n8n_execution_id: str | None,
    ) -> N8nWhatsAppInboundResponse:
        n8n_action = self._n8n_action(analysis.risk_level, payload.already_acted)
        return N8nWhatsAppInboundResponse(
            status="processed",
            request_id=request_id,
            n8n_execution_id=n8n_execution_id,
            case_id=case_id,
            risk_score=analysis.risk_score,
            risk_level=analysis.risk_level,
            n8n_action=n8n_action,
            user_message=analysis.whatsapp_user_message or analysis.user_message,
            trusted_contact_should_alert=analysis.trusted_circle_alert.should_alert,
            trusted_contact_message=analysis.whatsapp_trusted_contact_message
            or analysis.trusted_circle_alert.message,
            recovery_should_start=n8n_action == "start_recovery",
            report_summary=analysis.report.summary,
            safe_to_send=True,
            dry_run=config.dry_run,
        )

    def _save_state(
        self,
        *,
        payload: N8nWhatsAppInboundRequest,
        inbound_record: InboundMessageRecord,
        response: N8nWhatsAppInboundResponse,
        request_id: str | None,
        n8n_execution_id: str | None,
    ) -> None:
        self._state.cases.save(
            StateCase(
                case_id=response.case_id or f"n8n-case-{stable_hash(inbound_record.message_id)[:16]}",
                user_name=payload.user_name or "Pessoa protegida",
                channel=payload.channel,
                status=CaseProcessingStatus.OPEN,
                risk_score=response.risk_score,
                risk_level=response.risk_level,
                n8n_action=response.n8n_action,
                ruleset_version=config.ruleset_version,
                risk_engine_version=config.risk_engine_version,
            )
        )
        self._state.inbound_messages.mark_processed(
            inbound_record.message_id,
            case_id=response.case_id,
            response_json=response.model_dump(mode="json"),
        )
        self._state.audit_events.append(
            AuditEventRecord(
                case_id=response.case_id,
                request_id=request_id,
                n8n_execution_id=n8n_execution_id,
                event_type="n8n_whatsapp_inbound_processed",
                metadata={
                    "message_id": inbound_record.message_id,
                    "risk_score": response.risk_score,
                    "risk_level": response.risk_level,
                    "n8n_action": response.n8n_action,
                    "dry_run": config.dry_run,
                },
            )
        )

    def _reserve_inbound(
        self,
        payload: N8nWhatsAppInboundRequest,
        message_id: str,
        n8n_execution_id: str | None,
    ) -> tuple[InboundMessageRecord, bool]:
        record = InboundMessageRecord(
            message_id=message_id,
            channel=payload.channel,
            from_number_hash=stable_hash(payload.from_number),
            message_hash=stable_hash(payload.message),
            message_preview=message_preview(payload.message, store_full_message=config.store_full_message),
            n8n_execution_id=n8n_execution_id,
            processing_status=InboundProcessingStatus.RECEIVED,
        )
        existing, reserved = self._state.inbound_messages.reserve(record)
        return existing, reserved

    def _message_id(self, payload: N8nWhatsAppInboundRequest) -> str:
        if payload.message_id and payload.message_id.strip():
            return payload.message_id.strip()
        fingerprint = stable_hash(f"{payload.from_number or 'unknown'}:{payload.message}")[:24]
        return f"n8n-{fingerprint}"

    def _infer_action_type(self, message: str) -> str:
        normalized = normalize_text(message)
        if "pix" in normalized or "pagamento" in normalized or "transfer" in normalized:
            return "pix"
        if "link" in normalized or "http" in normalized or "www" in normalized:
            return "link"
        if "codigo" in normalized or "sms" in normalized or "token" in normalized or "senha" in normalized:
            return "codigo"
        if "taxa" in normalized or "emprego" in normalized:
            return "taxa"
        return "mensagem"

    def _n8n_action(self, risk_level: str, already_acted: bool) -> str:
        if already_acted:
            return "start_recovery"
        normalized = normalize_text(risk_level)
        if normalized in {"critical", "critico"}:
            return "alert_trusted_contact"
        if normalized in {"high", "alto"}:
            return "activate_trust_lock"
        if normalized in {"medium", "medio"}:
            return "ask_for_confirmation"
        return "allow_with_warning"
