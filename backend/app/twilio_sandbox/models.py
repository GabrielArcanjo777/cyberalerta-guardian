from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class TwilioSandboxOutboundRecord(BaseModel):
    provider_message_id: str
    to_address_masked: str
    kind: str
    status: str
    retryable: bool
    simulated: bool
    related_case_id: Optional[str] = None


class TwilioSandboxInboundWebhookResponse(BaseModel):
    provider: str
    duplicate: bool
    provider_message_id: str
    message_id: Optional[str]
    risk_assessment_id: Optional[str]
    risk_score: Optional[int]
    risk_level: Optional[str]
    case_id: Optional[str]
    case_created: bool
    protected_reply_sent: bool
    guardian_notified: bool
    outbound_messages: List[TwilioSandboxOutboundRecord] = Field(default_factory=list)
    events: List[str] = Field(default_factory=list)


class TwilioSandboxStatusCallbackResponse(BaseModel):
    provider: str
    provider_message_id: str
    status: str
    retryable: bool
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    event_id: str


class TwilioSandboxHealthResponse(BaseModel):
    provider: str
    mode: str
    production: bool
    channel_provider: str
    account_sid_configured: bool
    auth_token_configured: bool
    whatsapp_from_configured: bool
    guardian_address_configured: bool
    signature_validation_enabled: bool
    signature_secret_configured: bool
    network_send_ready: bool
    delivery_records: int
