"""Device-side authentication (Sprint 2, Unidade 4).

DeviceSession.id is the bearer credential a paired device presents on every
subsequent call — 122 bits of entropy from new_id(), same trust level as the
pairing token. Revocation (Unidade 5) works by flipping revoked_at, checked
here on every request, independent of whether the device is online.
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, Request, status

from app.devices.models import Device, DeviceState, utc_now
from app.devices.repository import DeviceRepository, get_device_repository

DEVICE_SESSION_HEADER = "X-Device-Session"


def require_device_session(
    request: Request,
    repository: DeviceRepository = Depends(get_device_repository),
) -> Device:
    session_id = request.headers.get(DEVICE_SESSION_HEADER)
    if not session_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    session = repository.get_session(session_id)
    if session is None or session.revoked_at is not None or session.expires_at < utc_now():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    device = repository.get_device(session.device_id)
    if device is None or device.state == DeviceState.REVOKED:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    repository.update_session(session.model_copy(update={"last_used_at": utc_now()}))
    return device
