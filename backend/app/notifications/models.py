from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex}"


class AlertType(str, Enum):
    TEST = "test"
    CASE_ALERT = "case_alert"


class AlertState(str, Enum):
    """Plano Mestre v1.1, Secao 4.5 — estados recomendados de Alerta."""

    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    ACTIONED = "actioned"
    FAILED = "failed"
    EXPIRED = "expired"


class AckEvent(str, Enum):
    DELIVERED = "delivered"
    OPENED = "opened"
    ACTIONED = "actioned"


class Alert(BaseModel):
    """``id`` doubles as the push payload's ``alert_id`` (Secao 7.2). The push
    itself never carries anything beyond alert_id/severity/alias/deep_link —
    everything else here is server-side bookkeeping the device never sees."""

    id: str = Field(default_factory=lambda: new_id("alert"))
    organization_id: str
    device_id: str
    type: AlertType = AlertType.TEST
    severity: str = Field(default="INFO", max_length=20)
    protected_person_alias: Optional[str] = Field(default=None, max_length=120)
    case_id: Optional[str] = None
    deep_link: str = Field(min_length=1, max_length=300)
    state: AlertState = AlertState.PENDING
    retry_count: int = 0
    failed_reason: Optional[str] = Field(default=None, max_length=200)
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    actioned_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
