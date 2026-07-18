from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import require_role
from app.auth.models import AuthUser, UserRole
from app.devices.device_auth import require_device_session
from app.devices.models import Device
from app.devices.service import ActorOrganizationRequiredError, DeviceNotFoundError
from app.notifications.schemas import AckRequest, AckResponse, TestPushResponse
from app.notifications.service import AlertNotFoundError, NotificationService, create_notification_service

_require_operator = require_role([UserRole.ADMIN, UserRole.ANALYST])


def get_notification_service() -> NotificationService:
    return create_notification_service()


def create_notifications_router() -> APIRouter:
    router = APIRouter(tags=["notifications"])

    @router.post("/devices/{device_id}/test-push", response_model=TestPushResponse)
    def send_test_push(
        device_id: str,
        actor: AuthUser = Depends(_require_operator),
        service: NotificationService = Depends(get_notification_service),
    ) -> TestPushResponse:
        try:
            alert = service.send_test_push(actor=actor, device_id=device_id)
        except ActorOrganizationRequiredError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from exc
        except DeviceNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        return TestPushResponse(alert_id=alert.id, state=alert.state, failed_reason=alert.failed_reason)

    @router.post("/devices/me/alerts/{alert_id}/ack", response_model=AckResponse)
    def acknowledge_alert(
        alert_id: str,
        payload: AckRequest,
        device: Device = Depends(require_device_session),
        service: NotificationService = Depends(get_notification_service),
    ) -> AckResponse:
        try:
            alert = service.acknowledge(device=device, alert_id=alert_id, event=payload.event)
        except AlertNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        return AckResponse(alert_id=alert.id, state=alert.state)

    return router
