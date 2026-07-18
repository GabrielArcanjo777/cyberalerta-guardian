from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import require_role
from app.auth.models import AuthUser, UserRole
from app.devices.device_auth import require_device_session
from app.devices.models import Device, PushToken
from app.devices.repository import DeviceRepository, get_device_repository
from app.devices.schemas import (
    CreatePairingInvitationRequest,
    CreatePairingInvitationResponse,
    DeviceItem,
    DeviceListResponse,
    PairDeviceRequest,
    PairDeviceResponse,
    RegisterPushTokenRequest,
    StatusResponse,
)
from app.devices.service import (
    ActorOrganizationRequiredError,
    DeviceNotFoundError,
    DeviceService,
    PairingInvitationExpiredError,
    PairingInvitationInvalidError,
    PairingInvitationTargetError,
)

_require_operator = require_role([UserRole.ADMIN, UserRole.ANALYST])


def get_device_service() -> DeviceService:
    return DeviceService()


def create_devices_router() -> APIRouter:
    router = APIRouter(tags=["devices"])

    @router.post("/devices/pairing-invitations", response_model=CreatePairingInvitationResponse)
    def create_pairing_invitation(
        payload: CreatePairingInvitationRequest,
        actor: AuthUser = Depends(_require_operator),
        service: DeviceService = Depends(get_device_service),
    ) -> CreatePairingInvitationResponse:
        try:
            invitation, token = service.create_pairing_invitation(
                actor=actor,
                trusted_contact_user_id=payload.trusted_contact_user_id,
                ttl_minutes=payload.ttl_minutes,
            )
        except ActorOrganizationRequiredError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from exc
        except PairingInvitationTargetError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        return CreatePairingInvitationResponse(
            invitation_id=invitation.id,
            token=token,
            expires_at=invitation.expires_at,
        )

    @router.post("/devices/pair", response_model=PairDeviceResponse)
    def pair_device(
        payload: PairDeviceRequest,
        service: DeviceService = Depends(get_device_service),
    ) -> PairDeviceResponse:
        try:
            device, session = service.pair_device(
                token=payload.token,
                platform=payload.platform,
                public_key=payload.public_key,
            )
        except (PairingInvitationInvalidError, PairingInvitationExpiredError) as exc:
            # Same status for "unknown", "used" and "expired" — an attacker
            # probing tokens learns nothing beyond "this one doesn't work".
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        return PairDeviceResponse(device_id=device.id, session_id=session.id, state=device.state)

    @router.get("/devices", response_model=DeviceListResponse)
    def list_devices(
        actor: AuthUser = Depends(_require_operator),
        service: DeviceService = Depends(get_device_service),
    ) -> DeviceListResponse:
        try:
            devices = service.list_devices(actor=actor)
        except ActorOrganizationRequiredError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from exc
        return DeviceListResponse(devices=[DeviceItem.model_validate(d.model_dump()) for d in devices])

    @router.get("/devices/{device_id}", response_model=DeviceItem)
    def get_device(
        device_id: str,
        actor: AuthUser = Depends(_require_operator),
        service: DeviceService = Depends(get_device_service),
    ) -> DeviceItem:
        try:
            device = service.get_device(actor=actor, device_id=device_id)
        except ActorOrganizationRequiredError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from exc
        except DeviceNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        return DeviceItem.model_validate(device.model_dump())

    @router.post("/devices/me/push-token", response_model=StatusResponse)
    def register_push_token(
        payload: RegisterPushTokenRequest,
        device: Device = Depends(require_device_session),
        repository: DeviceRepository = Depends(get_device_repository),
    ) -> StatusResponse:
        repository.upsert_push_token(PushToken(device_id=device.id, token=payload.token))
        return StatusResponse()

    return router
