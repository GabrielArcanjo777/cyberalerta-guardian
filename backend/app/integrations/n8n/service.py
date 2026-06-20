from __future__ import annotations

import logging
import uuid

from app.agents.orchestrator import GuardianOrchestrator
from app.core.config import config
from app.core.logging import get_logger, structured_log
from app.core.masking import mask_message, mask_phone
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
from app.repositories import OperationalStateRepository
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.schemas.recovery import RecoveryRequest
from app.services.text_normalization import normalize_text

from .schemas import (
    N8nGuardianFeedbackRequest,
    N8nGuardianFeedbackResponse,
    N8nHealthResponse,
    N8nRecoveryRequest,
    N8nRecoveryResponse,
    N8nWhatsAppInboundRequest,
    N8nWhatsAppInboundResponse,
)

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
            status="ok",
            integration="n8n",
            mode="beta",
            real_whatsapp_send_enabled=config.beta_real_send_enabled,
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
            from_number=mask_phone(payload.from_number),
            message=mask_message(payload.message),
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
            safe_to_send=response.safe_to_send,
            send_mode=response.send_mode,
        )
        return response

    def handle_recovery(
        self,
        payload: N8nRecoveryRequest,
        *,
        request_id: str | None,
        n8n_execution_id: str | None,
    ) -> N8nRecoveryResponse:
        recovery = self._orchestrator.run_recovery(self._recovery_request(payload, n8n_execution_id))
        case_id = payload.case_id or f"n8n-recovery-{stable_hash(str(uuid.uuid4()))[:16]}"
        self._state.audit_events.append(
            AuditEventRecord(
                case_id=case_id,
                request_id=request_id,
                n8n_execution_id=n8n_execution_id,
                event_type="n8n_recovery_requested",
                metadata={
                    "incident_type": recovery.incident_type,
                    "source": payload.source,
                    "n8n_action": recovery.n8n_action,
                },
            )
        )
        structured_log(
            logger,
            "n8n_recovery_prepared",
            request_id=request_id,
            n8n_execution_id=n8n_execution_id,
            case_id=case_id,
            incident_type=recovery.incident_type,
            n8n_action=recovery.n8n_action,
        )
        send_mode = self._resolve_send_mode(payload.reply_to_number)
        safe_to_send = send_mode == "real_beta_allowed"
        return N8nRecoveryResponse(
            status="processed",
            request_id=request_id,
            n8n_execution_id=n8n_execution_id,
            case_id=case_id,
            summary=recovery.summary,
            whatsapp_summary_message=recovery.whatsapp_summary_message,
            immediate_steps=recovery.immediate_steps,
            disclaimer=recovery.disclaimer,
            n8n_action=recovery.n8n_action,
            safe_to_send=safe_to_send,
            send_mode=send_mode,
            blocked_reason=self._blocked_reason(send_mode, payload.reply_to_number),
        )

    def handle_guardian_feedback(
        self,
        payload: N8nGuardianFeedbackRequest,
        *,
        request_id: str | None,
        n8n_execution_id: str | None,
    ) -> N8nGuardianFeedbackResponse:
        event = self._state.audit_events.append(
            AuditEventRecord(
                case_id=payload.case_id,
                request_id=request_id,
                n8n_execution_id=n8n_execution_id,
                event_type="n8n_guardian_feedback_received",
                metadata={
                    "message_id": payload.message_id,
                    "feedback_type": payload.feedback_type,
                    "notes": payload.notes,
                },
            )
        )
        structured_log(
            logger,
            "n8n_guardian_feedback_received",
            request_id=request_id,
            n8n_execution_id=n8n_execution_id,
            case_id=payload.case_id,
            message_id=payload.message_id,
            feedback_type=payload.feedback_type,
            stored=True,
        )
        return N8nGuardianFeedbackResponse(
            request_id=request_id,
            n8n_execution_id=n8n_execution_id,
            stored=True,
            event_id=event.event_id,
        )

    # --- Private helpers ---

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

    def _recovery_request(self, payload: N8nRecoveryRequest, n8n_execution_id: str | None) -> RecoveryRequest:
        paid = payload.already_paid or payload.incident_type == "pix_sent"
        return RecoveryRequest(
            paid=paid,
            clicked_link=payload.clicked_link,
            shared_documents=payload.shared_documents,
            shared_password=payload.shared_password,
            installed_app=payload.installed_app,
            shared_sms_code=payload.shared_sms_code,
            incident_type=payload.incident_type,
            already_paid=payload.already_paid,
            amount=payload.amount,
            payment_method=payload.payment_method,
            bank_name=payload.bank_name,
            has_shared_password=payload.shared_password,
            has_installed_remote_app=payload.installed_app,
            has_clicked_link=payload.clicked_link,
            has_sent_code=payload.shared_sms_code,
            source=payload.source,
            n8n_execution_id=n8n_execution_id,
            case_id=payload.case_id,
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
        reply_to = payload.reply_to_number or payload.from_number
        send_mode = self._resolve_send_mode(reply_to)
        safe_to_send = send_mode == "real_beta_allowed"
        user_msg = getattr(analysis, "whatsapp_user_message", None) or analysis.user_message
        tc_msg = getattr(analysis, "whatsapp_trusted_contact_message", None) or analysis.trusted_circle_alert.message
        return N8nWhatsAppInboundResponse(
            status="processed",
            request_id=request_id,
            n8n_execution_id=n8n_execution_id,
            case_id=case_id,
            risk_score=analysis.risk_score,
            risk_level=analysis.risk_level,
            n8n_action=n8n_action,
            user_message=user_msg,
            reply_to_number=reply_to,
            trusted_contact_should_alert=analysis.trusted_circle_alert.should_alert,
            trusted_contact_message=tc_msg,
            trusted_contact_phone=payload.trusted_contact_phone,
            recovery_should_start=n8n_action == "start_recovery",
            report_summary=analysis.report.summary,
            safe_to_send=safe_to_send,
            send_mode=send_mode,
            blocked_reason=self._blocked_reason(send_mode, reply_to),
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
                    "safe_to_send": response.safe_to_send,
                    "send_mode": response.send_mode,
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

    def _resolve_send_mode(self, reply_to: str | None) -> str:
        if not config.beta_real_send_enabled:
            return "dry_run"
        if not reply_to:
            return "dry_run"
        if config.beta_require_allowed_recipient:
            if reply_to in config.beta_allowed_recipients:
                return "real_beta_allowed"
            return "real_beta_blocked"
        return "real_beta_allowed"

    def _blocked_reason(self, send_mode: str, reply_to: str | None) -> str | None:
        if send_mode == "dry_run":
            return "BETA_REAL_SEND_ENABLED is false"
        if send_mode == "real_beta_blocked":
            return f"Recipient {mask_phone(reply_to)} not in BETA_ALLOWED_RECIPIENTS"
        return None
