from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class N8nWhatsAppInboundRequest(BaseModel):
    message_id: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("message_id", "messageId", "providerMessageId", "external_message_id"),
        max_length=180,
    )
    from_number: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("from_number", "from", "sender", "phone_hash"),
        max_length=180,
    )
    user_name: Optional[str] = Field(default=None, max_length=160)
    message: str = Field(validation_alias=AliasChoices("message", "body", "text"), min_length=1, max_length=8000)
    channel: str = Field(default="whatsapp", max_length=80)
    action_type: Optional[str] = Field(default=None, max_length=80)
    already_acted: bool = False
    trusted_contact_name: Optional[str] = Field(default=None, max_length=160)
    trusted_contact_relation: Optional[str] = Field(default=None, max_length=120)
    trusted_contact_phone: Optional[str] = Field(default=None, max_length=180)
    reply_to_number: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("reply_to_number", "replyTo", "reply_to"),
        max_length=180,
    )
    raw_payload: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(populate_by_name=True)


class N8nWhatsAppInboundResponse(BaseModel):
    status: str
    request_id: Optional[str] = None
    n8n_execution_id: Optional[str] = None
    case_id: Optional[str] = None

    risk_score: int
    risk_level: str
    n8n_action: str

    user_message: str
    reply_to_number: Optional[str] = None

    trusted_contact_should_alert: bool
    trusted_contact_message: Optional[str] = None
    trusted_contact_phone: Optional[str] = None

    recovery_should_start: bool = False
    report_summary: Optional[str] = None

    safe_to_send: bool
    send_mode: str
    blocked_reason: Optional[str] = None


class N8nHealthResponse(BaseModel):
    status: str = "ok"
    integration: str = "n8n"
    service: str = "n8n-integration"
    mode: str = "beta"
    real_whatsapp_send_enabled: bool = False
    whatsapp_inbound_endpoint: str = "/integrations/n8n/whatsapp/inbound"
    auth_header: str = "X-N8N-CyberAlerta-Secret"
    production: bool = False
    dry_run: bool = True


class N8nRecoveryRequest(BaseModel):
    incident_type: Optional[str] = Field(default=None, max_length=80)
    already_paid: bool = False
    source: str = Field(default="whatsapp", max_length=120)
    case_id: Optional[str] = Field(default=None, max_length=180)
    clicked_link: bool = False
    shared_documents: bool = False
    shared_password: bool = False
    installed_app: bool = False
    shared_sms_code: bool = False
    amount: Optional[float] = Field(default=None, ge=0)
    payment_method: Optional[str] = Field(default=None, max_length=80)
    bank_name: Optional[str] = Field(default=None, max_length=120)
    reply_to_number: Optional[str] = Field(default=None, max_length=180)
    raw_payload: Optional[Dict[str, Any]] = None


class N8nRecoveryResponse(BaseModel):
    status: str
    request_id: Optional[str] = None
    n8n_execution_id: Optional[str] = None
    case_id: Optional[str] = None
    summary: str
    whatsapp_summary_message: str
    immediate_steps: list[str]
    disclaimer: str
    n8n_action: str
    safe_to_send: bool
    send_mode: str
    blocked_reason: Optional[str] = None


class N8nGuardianFeedbackRequest(BaseModel):
    case_id: str = Field(min_length=1, max_length=180)
    message_id: Optional[str] = Field(default=None, max_length=180)
    feedback_type: str = Field(min_length=1, max_length=120)
    notes: Optional[str] = Field(default=None, max_length=1000)
    raw_payload: Optional[Dict[str, Any]] = None


class N8nGuardianFeedbackResponse(BaseModel):
    status: str = "ok"
    request_id: Optional[str] = None
    n8n_execution_id: Optional[str] = None
    stored: bool
    event_id: Optional[str] = None
