from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class EvolutionDemoOutboundRecord(BaseModel):
    provider_message_id: str
    to_address_masked: str
    kind: str
    status: str
    retryable: bool
    simulated: bool
    related_case_id: Optional[str] = None


class EvolutionDemoWebhookResponse(BaseModel):
    provider: str
    accepted: bool
    ignored: bool = False
    duplicate: bool
    provider_message_id: Optional[str] = None
    message_id: Optional[str] = None
    risk_assessment_id: Optional[str] = None
    risk_score: Optional[int] = None
    risk_level: Optional[str] = None
    case_id: Optional[str] = None
    case_created: bool
    guardian_notified: bool
    outbound_messages: List[EvolutionDemoOutboundRecord] = Field(default_factory=list)
    events: List[str] = Field(default_factory=list)
    demo_notice: str = (
        "EvolutionDemoAdapter is for local development, technical demos and portfolio validation only."
    )


class EvolutionDemoHealthResponse(BaseModel):
    provider: str
    mode: str
    production: bool = False
    api_url_configured: bool
    api_key_configured: bool
    instance_name_configured: bool
    guardian_address_configured: bool
    network_send_ready: bool
    delivery_records: int
    demo_notice: str = (
        "Evolution API is not an official production WhatsApp Business integration."
    )
