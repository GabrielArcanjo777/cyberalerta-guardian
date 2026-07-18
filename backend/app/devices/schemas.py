from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.devices.models import DevicePlatform, DeviceState


class CreatePairingInvitationRequest(BaseModel):
    trusted_contact_user_id: str = Field(min_length=1)
    ttl_minutes: int = Field(default=15, ge=1, le=120)


class CreatePairingInvitationResponse(BaseModel):
    invitation_id: str
    token: str
    expires_at: datetime


class PairDeviceRequest(BaseModel):
    token: str = Field(min_length=1)
    platform: DevicePlatform
    public_key: str = Field(min_length=1, max_length=2000)


class PairDeviceResponse(BaseModel):
    device_id: str
    session_id: str
    state: DeviceState


class DeviceItem(BaseModel):
    id: str
    user_id: str
    platform: DevicePlatform
    state: DeviceState
    last_seen_at: Optional[datetime] = None
    created_at: datetime


class DeviceListResponse(BaseModel):
    devices: list[DeviceItem]
