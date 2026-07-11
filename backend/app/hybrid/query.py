from __future__ import annotations

from typing import Any, Dict, Optional

from app.event_model import EventModelService
from app.event_model.models import BotEventType

_DECISION_EVENTS = {
    BotEventType.HYBRID_DECISION_CREATED,
    BotEventType.HYBRID_SHADOW_DECISION_CREATED,
}


def get_hybrid_decision_for_case(
    event_model: EventModelService, case_id: str
) -> Optional[Dict[str, Any]]:
    """Return the most recent hybrid decision payload for a case, or None.

    Reads it straight from the persisted event trail (no new storage). The
    payload is already audit-safe: hashes, scores, versions, reasons — never
    raw content or secrets.
    """
    if not case_id:
        return None
    # events are appended in chronological order; the last match is the latest.
    latest = None
    for event in event_model.repositories.events.list_all():
        if event.case_id == case_id and event.event_type in _DECISION_EVENTS:
            latest = event
    if latest is None:
        return None
    payload = dict(latest.payload)
    payload["event_type"] = latest.event_type.value
    payload["occurred_at"] = latest.occurred_at.isoformat()
    return payload
