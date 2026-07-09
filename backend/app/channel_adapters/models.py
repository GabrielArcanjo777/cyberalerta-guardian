from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from app.event_model import ChannelConnection


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_channel_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex}"


class ChannelProvider(str, Enum):
    MOCK_WHATSAPP = "mock_whatsapp"
    EVOLUTION_DEMO = "evolution_demo"
    META_CLOUD_API = "meta_cloud_api"
    MOCK = "mock"


class DeliveryStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"


class OutboundMessageKind(str, Enum):
    PROTECTED_REPLY = "protected_reply"
    GUARDIAN_ALERT = "guardian_alert"


class NormalizedMedia(BaseModel):
    media_type: str = Field(alias="type", min_length=1, max_length=80)
    url: Optional[str] = None
    provider_media_id: Optional[str] = Field(default=None, alias="providerMediaId")

    model_config = ConfigDict(populate_by_name=True)


class InboundMessage(BaseModel):
    id: str = Field(default_factory=lambda: new_channel_id("inbound"), min_length=1, max_length=180)
    provider: ChannelProvider
    external_message_id: str = Field(
        min_length=1,
        max_length=180,
        validation_alias=AliasChoices("externalMessageId", "providerMessageId", "provider_message_id"),
        serialization_alias="externalMessageId",
    )
    from_address: str = Field(
        min_length=1,
        max_length=180,
        validation_alias=AliasChoices("from", "from_address"),
        serialization_alias="from",
    )
    to_address: str = Field(
        min_length=1,
        max_length=180,
        validation_alias=AliasChoices("to", "to_address"),
        serialization_alias="to",
    )
    body: str = Field(min_length=1, max_length=8000)
    timestamp: datetime
    profile_name: Optional[str] = Field(default=None, alias="profileName", max_length=180)
    media: List[NormalizedMedia] = Field(default_factory=list)
    raw_payload: Any = Field(
        default_factory=dict,
        validation_alias=AliasChoices("rawPayload", "raw", "raw_payload"),
        serialization_alias="rawPayload",
    )
    normalized_at: datetime = Field(
        default_factory=utc_now,
        validation_alias=AliasChoices("normalizedAt", "normalized_at"),
        serialization_alias="normalizedAt",
    )
    protected_person_id: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("protectedPersonId", "protected_person_id"),
        serialization_alias="protectedPersonId",
    )
    case_id: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("caseId", "case_id"),
        serialization_alias="caseId",
    )

    model_config = ConfigDict(populate_by_name=True)

    @property
    def provider_message_id(self) -> str:
        return self.external_message_id

    @property
    def raw(self) -> Any:
        return self.raw_payload


NormalizedInboundMessage = InboundMessage


class OutboundMessage(BaseModel):
    id: str = Field(default_factory=lambda: new_channel_id("outbound"), min_length=1, max_length=180)
    provider: ChannelProvider
    to_address: str = Field(
        min_length=1,
        max_length=180,
        validation_alias=AliasChoices("to", "to_address"),
        serialization_alias="to",
    )
    body: str = Field(min_length=1, max_length=4000)
    template_name: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("templateName", "template_name"),
        serialization_alias="templateName",
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)
    case_id: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("caseId", "case_id", "relatedCaseId", "related_case_id"),
        serialization_alias="caseId",
    )
    protected_person_id: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("protectedPersonId", "protected_person_id"),
        serialization_alias="protectedPersonId",
    )

    model_config = ConfigDict(populate_by_name=True)


class OutboundMessageRequest(OutboundMessage):
    kind: OutboundMessageKind
    related_message_id: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("relatedMessageId", "related_message_id"),
        serialization_alias="relatedMessageId",
    )

    model_config = ConfigDict(populate_by_name=True)

    @property
    def related_case_id(self) -> Optional[str]:
        return self.case_id


class OutboundMessageResult(BaseModel):
    provider: ChannelProvider
    provider_message_id: str = Field(alias="providerMessageId", min_length=1, max_length=180)
    to_address: str = Field(alias="to", min_length=1, max_length=180)
    status: DeliveryStatus = DeliveryStatus.PENDING
    simulated: bool = True
    retryable: bool = False
    retry_after_seconds: Optional[int] = Field(default=None, alias="retryAfterSeconds", ge=0)
    raw: Any = None

    model_config = ConfigDict(populate_by_name=True)


class DeliveryStatusEvent(BaseModel):
    provider: ChannelProvider
    external_message_id: str = Field(
        min_length=1,
        max_length=180,
        validation_alias=AliasChoices("externalMessageId", "providerMessageId", "provider_message_id"),
        serialization_alias="externalMessageId",
    )
    status: DeliveryStatus
    timestamp: datetime
    error_code: Optional[str] = Field(default=None, alias="errorCode")
    error_message: Optional[str] = Field(default=None, alias="errorMessage")
    retryable: bool = False
    raw_payload: Any = Field(
        default=None,
        validation_alias=AliasChoices("rawPayload", "raw", "raw_payload"),
        serialization_alias="rawPayload",
    )

    model_config = ConfigDict(populate_by_name=True)

    @property
    def provider_message_id(self) -> str:
        return self.external_message_id

    @property
    def raw(self) -> Any:
        return self.raw_payload


class ChannelConnectionValidation(BaseModel):
    provider: ChannelProvider
    valid: bool
    connection_id: Optional[str] = Field(default=None, alias="connectionId")
    message: Optional[str] = None
    checked_at: datetime = Field(default_factory=utc_now, alias="checkedAt")

    model_config = ConfigDict(populate_by_name=True)


class ChannelReceiveResult(BaseModel):
    inbound: InboundMessage
    accepted: bool = True
    duplicate: bool = False
    message: Optional[str] = None


class ChannelOutboundResult(BaseModel):
    outbound: OutboundMessage
    result: OutboundMessageResult


class ChannelIngressResult(BaseModel):
    inbound: InboundMessage
    duplicate: bool
    message_id: Optional[str] = None
    risk_assessment_id: Optional[str] = None
    case_id: Optional[str] = None
    emitted_event_ids: List[str] = Field(default_factory=list)
