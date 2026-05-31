from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.trusted_circle.trusted_circle_models import TrustedCircleEscalationRecord

_LOG: Dict[str, TrustedCircleEscalationRecord] = {}


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def save(record: TrustedCircleEscalationRecord) -> TrustedCircleEscalationRecord:
    _LOG[record.escalation_id] = record
    return record


def get(escalation_id: str) -> Optional[TrustedCircleEscalationRecord]:
    return _LOG.get(escalation_id)


def list_all() -> List[TrustedCircleEscalationRecord]:
    return sorted(_LOG.values(), key=lambda item: item.created_at, reverse=True)


def count() -> int:
    return len(_LOG)


def latest_for_case(case_id: str) -> Optional[TrustedCircleEscalationRecord]:
    matches = [item for item in _LOG.values() if item.case_id == case_id]
    if not matches:
        return None
    return max(matches, key=lambda item: item.created_at)
