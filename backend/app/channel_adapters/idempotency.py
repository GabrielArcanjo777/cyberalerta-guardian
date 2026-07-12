from __future__ import annotations

import time
from collections import OrderedDict
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
    """Idempotency guard for inbound provider messages.

    Entries carry the ``time.monotonic()`` timestamp of their **first**
    reception.  Duplicate messages within *ttl_seconds* are rejected without
    renewing the timer.  After the TTL elapses the same external message is
    accepted again (it may be a genuine resend, not a replay).

    The registry is bounded to *max_size* entries; when full the oldest entry
    (by insertion order) is evicted before the new one is stored.

    Thread-safe (``RLock``).  ``has_seen`` is a pure read — it never mutates
    the registry.

    .. note::
       This is an in-memory MVP. For production with multiple workers or
       restarts, use a persistent store (Redis SET NX EX, a database ``INSERT
       … ON CONFLICT`` with a TTL column, etc.). The in-process set is lost on
       restart, so duplicate delivery across process boundaries is not
       prevented by this class alone.
    """

    # Defaults tuned for a single-process MVP: one hour of history, up to
    # 100 000 entries. At ~120 bytes per tuple + timestamp that is ~12 MiB.
    DEFAULT_MAX_SIZE = 100_000
    DEFAULT_TTL_SECONDS = 3600  # 1 hour

    def __init__(
        self,
        *,
        max_size: int = DEFAULT_MAX_SIZE,
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
    ) -> None:
        if max_size < 1:
            raise ValueError("max_size must be >= 1")
        if ttl_seconds < 1:
            raise ValueError("ttl_seconds must be >= 1")
        self._max_size = max_size
        self._ttl = ttl_seconds
        self._seen: OrderedDict[ProviderMessageKey, float] = OrderedDict()
        self._lock = RLock()

    # -- public -----------------------------------------------------------------

    def register_inbound(self, inbound: InboundMessage) -> bool:
        """Register *inbound* and return ``True`` if it was first seen.

        Returns ``False`` when the message was already registered AND its
        registration is still within the TTL window — i.e. it is a real
        duplicate.  Expired entries are silently removed and the message is
        accepted as new.
        """
        key = (inbound.provider, inbound.provider_message_id)
        with self._lock:
            now = time.monotonic()
            existing = self._seen.get(key)
            if existing is not None:
                if (now - existing) < self._ttl:
                    # Duplicate within TTL — reject without updating timestamp.
                    return False
                # Expired — remove the stale entry so the sweep below does not
                # accidentally evict it (it was already expired) and we can
                # re-insert with a fresh timestamp.
                del self._seen[key]
            # Evict any entries whose TTL has passed (oldest-first).
            self._sweep_expired(now)
            # Make room for one insert so len never exceeds max_size.
            while len(self._seen) >= self._max_size:
                self._seen.popitem(last=False)
            self._seen[key] = now
            return True

    def has_seen(self, provider: ChannelProvider, provider_message_id: str) -> bool:
        """Check whether *provider_message_id* is still within the TTL window.

        Pure read — never mutates the registry.
        """
        key = (provider, provider_message_id)
        with self._lock:
            ts = self._seen.get(key)
            if ts is None:
                return False
            return (time.monotonic() - ts) < self._ttl

    # -- internal ---------------------------------------------------------------

    def _sweep_expired(self, now: float) -> None:
        """Evict entries whose TTL has passed.

        Pops from the left (oldest insertion order) and stops at the first
        valid entry, so worst-case O(expired), common case O(1).  Called
        inside the lock.
        """
        while self._seen:
            _key, ts = next(iter(self._seen.items()))
            if now - ts >= self._ttl:
                self._seen.popitem(last=False)
            else:
                break


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
