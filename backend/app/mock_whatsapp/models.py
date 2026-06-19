from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class MockWhatsAppInboundRequest(BaseModel):
    provider_message_id: Optional[str] = Field(default=None, alias="providerMessageId", max_length=180)
    from_address: str = Field(default="+5511999990001", alias="from", min_length=1, max_length=180)
    to_address: str = Field(default="+5511999990000", alias="to", min_length=1, max_length=180)
    body: str = Field(min_length=1, max_length=8000)
    timestamp: Optional[datetime] = None
    protected_person_alias: str = Field(default="Dona Lucia", max_length=120)
    guardian_alias: str = Field(default="Gabriel", max_length=120)
    guardian_address: str = Field(default="+5511888880001", max_length=180)
    profile_name: Optional[str] = Field(default=None, alias="profileName", max_length=180)
    media: List[Dict[str, Any]] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)


class MockWhatsAppFixture(BaseModel):
    fixture_id: str
    title: str
    description: str
    request: MockWhatsAppInboundRequest
    expected: str


class MockOutboundRecord(BaseModel):
    provider_message_id: str
    to_address: str
    body: str
    kind: str
    status: str
    simulated: bool
    related_case_id: Optional[str] = None


class MockWhatsAppSimulationResponse(BaseModel):
    simulation_id: str
    duplicate: bool
    provider_message_id: str
    message_id: Optional[str]
    risk_assessment_id: Optional[str]
    risk_score: Optional[int]
    risk_level: Optional[str]
    case_id: Optional[str]
    case_created: bool
    guardian_notified: bool
    outbound_messages: List[MockOutboundRecord] = Field(default_factory=list)
    events: List[str] = Field(default_factory=list)


class MockWhatsAppFixturesResponse(BaseModel):
    fixtures: List[MockWhatsAppFixture]


class MockWhatsAppStateResponse(BaseModel):
    simulations: List[MockWhatsAppSimulationResponse]
    total: int
