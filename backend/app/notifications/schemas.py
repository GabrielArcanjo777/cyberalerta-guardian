from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from app.notifications.models import AckEvent, AlertState


class TestPushResponse(BaseModel):
    alert_id: str
    state: AlertState
    failed_reason: Optional[str] = None


class AckRequest(BaseModel):
    event: AckEvent


class AckResponse(BaseModel):
    alert_id: str
    state: AlertState
