from typing import List, Literal

from pydantic import BaseModel, Field


class SimpleChannelSubmitRequest(BaseModel):
    protected_person_alias: str = Field(min_length=1, max_length=120)
    channel: Literal["whatsapp_mock"] = "whatsapp_mock"
    content_type: Literal["text"] = "text"
    content: str = Field(min_length=1, max_length=4000)
    consent: bool


class SimpleChannelSubmitResponse(BaseModel):
    channel_case_id: str
    risk_level: str
    simple_reply: str
    admin_case_created: bool
    trust_lock_recommended: bool


class SimpleChannelStatusResponse(BaseModel):
    service: str
    mode: str
    channels: List[str]
    whatsapp_real_enabled: bool
    monitoring_enabled: bool
    privacy_note: str
    demo_note: str
