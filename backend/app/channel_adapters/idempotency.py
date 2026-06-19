from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from threading import RLock
from typing import Dict, Optional, Tuple

from app.channel_adapters.models import (
    ChannelProvider,
    DeliveryStatus,
    DeliveryStatusEvent,
    InboundMessage,
    OutboundMessageResult,
)

ProviderMessageKey = Tuple[ChannelProvider, str]


class InMemoryProviderMessageRegistry:
    def __init__(self) -> None:
        self._seen: set[ProviderMessageKey] = set()
        self._lock = RLock()

    def register_inbound(self, inbound: InboundMessage) -> bool:
        key = (inbound.provider, inbound.provider_message_id)
        with self._lock:
            if key in self._seen:
                return False
            self._seen.add(key)
            return True

    def has_seen(self, provider: ChannelProvider, provider_message_id: str) -> bool:
        with self._lock:
            return (provider, provider_message_id) in self._seen


@dataclass(frozen=True)
class DeliveryStatusRecord:
    provider: ChannelProvider
    provider_message_id: str
    status: DeliveryStatus
    updated_at: datetime
    retryable: bool
    error_code: Optional[str] = None
    error_message: Optional[str] = None


class InMemoryDeliveryStatusRegistry:
    def __init__(self) -> None:
        self._records: Dict[ProviderMessageKey, DeliveryStatusRecord] = {}
        self._lock = RLock()

    def record_outbound(self, result: OutboundMessageResult, updated_at: datetime) -> DeliveryStatusRecord:
        record = DeliveryStatusRecord(
            provider=result.provider,
            provider_message_id=result.provider_message_id,
            status=result.status,
            updated_at=updated_at,
            retryable=result.retryable,
        )
        with self._lock:
            self._records[(result.provider, result.provider_message_id)] = record
        return record

    def update_from_callback(self, event: DeliveryStatusEvent) -> DeliveryStatusRecord:
        record = DeliveryStatusRecord(
            provider=event.provider,
            provider_message_id=event.provider_message_id,
            status=event.status,
            updated_at=event.timestamp,
            retryable=event.retryable,
            error_code=event.error_code,
            error_message=event.error_message,
        )
        with self._lock:
            self._records[(event.provider, event.provider_message_id)] = record
        return record

    def get(self, provider: ChannelProvider, provider_message_id: str) -> Optional[DeliveryStatusRecord]:
        with self._lock:
            return self._records.get((provider, provider_message_id))
