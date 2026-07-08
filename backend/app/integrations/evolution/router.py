"""Routes to pair and monitor the Evolution (WhatsApp Web) channel.

Mounted under ``/api/channels/evolution``. Sensitive (pairing a WhatsApp number),
so gated by ``require_sensitive_access`` like the other operational routes.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.auth import require_sensitive_access
from app.integrations.evolution.instance_client import (
    EvolutionConnectionState,
    EvolutionInstanceClient,
)

router = APIRouter(tags=["evolution"])

_client: EvolutionInstanceClient | None = None


def get_evolution_instance_client() -> EvolutionInstanceClient:
    global _client
    if _client is None:
        _client = EvolutionInstanceClient()
    return _client


def set_evolution_instance_client(client: EvolutionInstanceClient | None) -> None:
    """Test seam to inject a fake-transport client."""
    global _client
    _client = client


@router.get("/status", response_model=EvolutionConnectionState)
def evolution_status(
    auto_reconnect: bool = Query(False, description="Reconnect automatically if the session dropped"),
    access: None = Depends(require_sensitive_access),
):
    client = get_evolution_instance_client()
    return client.ensure_connected() if auto_reconnect else client.connection_state()


@router.get("/qr", response_model=EvolutionConnectionState)
def evolution_qr(access: None = Depends(require_sensitive_access)):
    return get_evolution_instance_client().get_qr()


@router.post("/reconnect", response_model=EvolutionConnectionState)
def evolution_reconnect(access: None = Depends(require_sensitive_access)):
    return get_evolution_instance_client().reconnect()


def create_evolution_router() -> APIRouter:
    return router
