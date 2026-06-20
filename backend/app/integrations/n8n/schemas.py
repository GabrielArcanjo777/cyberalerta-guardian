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
    trusted_contact_should_alert: bool
    trusted_contact_message: Optional[str] = None
    recovery_should_start: bool = False
    report_summary: Optional[str] = None
    safe_to_send: bool = True
    dry_run: bool = True


class N8nHealthResponse(BaseModel):
    status: str = "ok"
    service: str = "n8n-integration"
    dry_run: bool
    whatsapp_inbound_endpoint: str = "/integrations/n8n/whatsapp/inbound"
    auth_header: str
    production: bool = False
