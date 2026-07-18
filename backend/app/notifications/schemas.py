from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.notifications.models import AckEvent, AlertState, AlertType


class TestPushResponse(BaseModel):
    alert_id: str
    state: AlertState
    failed_reason: Optional[str] = None


class AlertDetailResponse(BaseModel):
    alert_id: str
    type: AlertType
    severity: str
    protected_person_alias: Optional[str] = None
    case_id: Optional[str] = None
    deep_link: str
    state: AlertState
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    actioned_at: Optional[datetime] = None


class AckRequest(BaseModel):
    event: AckEvent


class AckResponse(BaseModel):
    alert_id: str
    state: AlertState
