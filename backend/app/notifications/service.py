"""Test-push send + ACK handling (Plano Mestre v1.1, Secao 4.3/6.2/7.2,
Sprint 2 Unidade 4). Sending a real CASE_ALERT tied to a Case is Sprint 5
(integracao ponta a ponta) — this unit only proves the channel works end to
end with a synthetic TEST alert, which is exactly what Secao 10.5 asks for
before any Windows work starts.
"""

from __future__ import annotations

import logging
from typing import Optional

from app.auth.models import AuthUser
from app.core.config import config
from app.devices.models import Device, DeviceState
from app.devices.repository import DeviceRepository, get_device_repository
from app.devices.service import DeviceService
from app.notifications.contract import PushProviderError, PushProviderTokenInvalid, PushSender
from app.notifications.models import AckEvent, Alert, AlertState, AlertType, utc_now
from app.notifications.repository import AlertRepository, get_notification_repository

logger = logging.getLogger("cyberalerta.notifications")

_ACK_STATE = {
    AckEvent.DELIVERED: AlertState.DELIVERED,
    AckEvent.OPENED: AlertState.OPENED,
    AckEvent.ACTIONED: AlertState.ACTIONED,
}
_STATE_RANK = {
    AlertState.PENDING: 0,
    AlertState.SENT: 1,
    AlertState.DELIVERED: 2,
    AlertState.OPENED: 3,
    AlertState.ACTIONED: 4,
}
_TEST_PUSH_DEEP_LINK = "cyberalerta://pair"


class AlertNotFoundError(Exception):
    """Alert does not exist, or does not belong to the requesting device —
    maps to 404, same non-disclosure spirit as DeviceNotFoundError."""


def _push_payload(alert: Alert) -> dict:
    return {
        "type": alert.type.value.upper(),
        "alert_id": alert.id,
        "case_id": alert.case_id,
        "severity": alert.severity,
        "protected_person_alias": alert.protected_person_alias,
        "deep_link": alert.deep_link,
        "sent_at": utc_now().isoformat(),
    }


class NotificationService:
    def __init__(
        self,
        repository: Optional[AlertRepository] = None,
        device_repository: Optional[DeviceRepository] = None,
        sender: Optional[PushSender] = None,
    ) -> None:
        self.repository = repository or get_notification_repository()
        self.device_repository = device_repository or get_device_repository()
        self.sender = sender
        self._devices = DeviceService(repository=self.device_repository)

    def send_test_push(self, *, actor: AuthUser, device_id: str) -> Alert:
        # Reuses DeviceService.get_device so a cross-org test-push attempt
        # fails exactly like the GET /devices/{id} IDOR case (404).
        device = self._devices.get_device(actor=actor, device_id=device_id)

        alert = self.repository.create_alert(
            Alert(
                organization_id=device.organization_id,
                device_id=device.id,
                type=AlertType.TEST,
                severity="INFO",
                deep_link=_TEST_PUSH_DEEP_LINK,
            )
        )

        if device.state == DeviceState.REVOKED:
            # Revocation already drops the push token, so this would fail
            # closed as "push_token_missing" anyway — naming it explicitly
            # makes the operator-facing reason honest about what happened.
            return self._fail(alert, "device_revoked")

        push_token = self.device_repository.get_push_token_by_device(device.id)
        if push_token is None:
            return self._fail(alert, "push_token_missing")
        if self.sender is None:
            return self._fail(alert, "fcm_not_configured")

        try:
            self.sender.send(token=push_token.token, payload=_push_payload(alert))
        except PushProviderTokenInvalid:
            self.device_repository.delete_push_token_by_device(device.id)
            return self._fail(alert, "invalid_token")
        except PushProviderError:
            logger.warning("Push provider error sending alert %s", alert.id)
            return self._fail(alert, "provider_error")

        return self.repository.update_alert(
            alert.model_copy(update={"state": AlertState.SENT, "sent_at": utc_now()})
        )

    def _fail(self, alert: Alert, reason: str) -> Alert:
        return self.repository.update_alert(
            alert.model_copy(update={"state": AlertState.FAILED, "failed_reason": reason})
        )

    def acknowledge(self, *, device: Device, alert_id: str, event: AckEvent) -> Alert:
        alert = self.repository.get_alert(alert_id)
        if alert is None or alert.device_id != device.id:
            raise AlertNotFoundError("Alert not found.")

        target_state = _ACK_STATE[event]
        if _STATE_RANK[target_state] > _STATE_RANK[alert.state]:
            timestamp_field = f"{event.value}_at"
            alert = self.repository.update_alert(
                alert.model_copy(update={"state": target_state, timestamp_field: utc_now()})
            )
        # else: stale/duplicate ACK replay — idempotent no-op, return as-is.

        if (
            alert.type == AlertType.TEST
            and target_state in (AlertState.OPENED, AlertState.ACTIONED)
            and device.state == DeviceState.PENDING_PAIRING
        ):
            self.device_repository.update_device(device.model_copy(update={"state": DeviceState.ACTIVE}))

        return alert


def _build_push_sender() -> Optional[PushSender]:
    if not (config.fcm_project_id and config.fcm_service_account_json):
        return None
    try:
        from app.notifications.providers.fcm_http_sender import FCMHttpSender

        return FCMHttpSender(
            project_id=config.fcm_project_id,
            service_account_json=config.fcm_service_account_json,
        )
    except PushProviderError:
        logger.warning("FCM configured but failed to initialize; push stays disabled.")
        return None


def create_notification_service() -> NotificationService:
    return NotificationService(sender=_build_push_sender())
