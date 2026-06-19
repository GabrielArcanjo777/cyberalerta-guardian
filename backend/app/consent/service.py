from __future__ import annotations

from app.consent.models import (
    DEFAULT_CONSENT_SCOPES,
    ConsentAcceptRequest,
    ConsentBotActivationRequest,
    ConsentEvent,
    ConsentEventType,
    ConsentRecord,
    ConsentRevokeRequest,
    ConsentScope,
    ConsentScopeUpdateRequest,
    ConsentStatusResponse,
    OptInStatus,
)
from app.event_model import BotEventType, LocalEventBus
from app.event_model.models import utc_now
from app.storage import consent_store


CONSENT_EVENT_MAP = {
    ConsentEventType.ACCEPTED: BotEventType.CONSENT_ACCEPTED,
    ConsentEventType.REVOKED: BotEventType.CONSENT_REVOKED,
    ConsentEventType.BOT_ACTIVATED: BotEventType.BOT_ACTIVATED,
    ConsentEventType.BOT_DEACTIVATED: BotEventType.BOT_DEACTIVATED,
    ConsentEventType.SCOPE_CHANGED: BotEventType.CONSENT_SCOPE_CHANGED,
}


class ConsentActivationError(ValueError):
    pass


class ConsentService:
    def __init__(self, event_bus: LocalEventBus | None = None) -> None:
        self._event_bus = event_bus

    def get_status(self, protected_person_id: str = "demo-protected-person") -> ConsentStatusResponse:
        record = self._get_or_create_record(protected_person_id=protected_person_id)
        events = consent_store.list_events(record.consent_id)
        return ConsentStatusResponse(
            record=record.model_copy(deep=True),
            latest_event=events[-1].model_copy(deep=True) if events else None,
            events=[event.model_copy(deep=True) for event in events[-10:]],
            can_activate_bot=record.status in {OptInStatus.ACTIVE, OptInStatus.BOT_DISABLED},
        )

    def accept(self, request: ConsentAcceptRequest) -> ConsentStatusResponse:
        record = consent_store.get_or_create_record(
            protected_person_id=request.protected_person_id,
            protected_person_alias=request.protected_person_alias,
            guardian_id=request.guardian_id,
            guardian_alias=request.guardian_alias,
            channel_provider=request.channel_provider,
        )
        now = utc_now()
        record.protected_person_alias = request.protected_person_alias
        record.guardian_id = request.guardian_id or record.guardian_id
        record.guardian_alias = request.guardian_alias or record.guardian_alias
        record.channel_provider = request.channel_provider or record.channel_provider
        record.status = OptInStatus.ACTIVE
        record.bot_active = True
        record.scopes = request.scopes or list(DEFAULT_CONSENT_SCOPES)
        record.accepted_at = record.accepted_at or now
        record.revoked_at = None
        record.updated_at = now
        consent_store.save_record(record)
        self._record_event(
            record=record,
            event_type=ConsentEventType.ACCEPTED,
            actor=request.actor,
            reason=request.reason,
            scopes=record.scopes,
        )
        self._record_event(
            record=record,
            event_type=ConsentEventType.BOT_ACTIVATED,
            actor=request.actor,
            reason="Bot ativado apos opt-in explicito.",
            scopes=record.scopes,
        )
        return self.get_status(record.protected_person_id)

    def revoke(self, request: ConsentRevokeRequest) -> ConsentStatusResponse:
        record = self._get_or_create_record(protected_person_id=request.protected_person_id)
        now = utc_now()
        record.status = OptInStatus.REVOKED
        record.bot_active = False
        record.revoked_at = now
        record.updated_at = now
        consent_store.save_record(record)
        self._record_event(
            record=record,
            event_type=ConsentEventType.REVOKED,
            actor=request.actor,
            reason=request.reason,
            scopes=record.scopes,
        )
        self._record_event(
            record=record,
            event_type=ConsentEventType.BOT_DEACTIVATED,
            actor=request.actor,
            reason="Bot desativado por revogacao de consentimento.",
            scopes=record.scopes,
        )
        return self.get_status(record.protected_person_id)

    def activate_bot(self, request: ConsentBotActivationRequest) -> ConsentStatusResponse:
        record = self._get_or_create_record(protected_person_id=request.protected_person_id)
        if record.status not in {OptInStatus.ACTIVE, OptInStatus.BOT_DISABLED} or not record.accepted_at:
            raise ConsentActivationError("Opt-in ativo e necessario antes de ativar o bot.")
        record.status = OptInStatus.ACTIVE
        record.bot_active = True
        record.updated_at = utc_now()
        consent_store.save_record(record)
        self._record_event(
            record=record,
            event_type=ConsentEventType.BOT_ACTIVATED,
            actor=request.actor,
            reason=request.reason or "Bot reativado pelo Console.",
            scopes=record.scopes,
        )
        return self.get_status(record.protected_person_id)

    def deactivate_bot(self, request: ConsentBotActivationRequest) -> ConsentStatusResponse:
        record = self._get_or_create_record(protected_person_id=request.protected_person_id)
        if record.status == OptInStatus.ACTIVE:
            record.status = OptInStatus.BOT_DISABLED
        record.bot_active = False
        record.updated_at = utc_now()
        consent_store.save_record(record)
        self._record_event(
            record=record,
            event_type=ConsentEventType.BOT_DEACTIVATED,
            actor=request.actor,
            reason=request.reason or "Bot desativado pelo Console sem revogar consentimento.",
            scopes=record.scopes,
        )
        return self.get_status(record.protected_person_id)

    def update_scopes(self, request: ConsentScopeUpdateRequest) -> ConsentStatusResponse:
        record = self._get_or_create_record(protected_person_id=request.protected_person_id)
        record.scopes = request.scopes
        record.updated_at = utc_now()
        consent_store.save_record(record)
        self._record_event(
            record=record,
            event_type=ConsentEventType.SCOPE_CHANGED,
            actor=request.actor,
            reason=request.reason,
            scopes=record.scopes,
        )
        return self.get_status(record.protected_person_id)

    def _get_or_create_record(
        self,
        *,
        protected_person_id: str,
        protected_person_alias: str = "Pessoa protegida",
        guardian_id: str | None = None,
        guardian_alias: str | None = None,
        channel_provider: str = "mock",
    ) -> ConsentRecord:
        return consent_store.get_or_create_record(
            protected_person_id=protected_person_id,
            protected_person_alias=protected_person_alias,
            guardian_id=guardian_id,
            guardian_alias=guardian_alias,
            channel_provider=channel_provider,
        )

    def _record_event(
        self,
        *,
        record: ConsentRecord,
        event_type: ConsentEventType,
        actor: str,
        reason: str | None,
        scopes: list[ConsentScope],
    ) -> ConsentEvent:
        event = ConsentEvent(
            consent_id=record.consent_id,
            event_type=event_type,
            actor=actor,
            scopes=scopes,
            reason=reason,
        )
        consent_store.append_event(event)
        if self._event_bus is not None:
            self._event_bus.publish_type(
                CONSENT_EVENT_MAP[event_type],
                aggregate_type="consent",
                aggregate_id=record.consent_id,
                source="consent_service",
                actor=actor,
                protected_person_id=record.protected_person_id,
                payload={
                    "consent_event": event.model_dump(mode="json"),
                    "consent_record": record.model_dump(mode="json"),
                    "reason": reason,
                    "bot_active": record.bot_active,
                    "status": record.status.value,
                    "scopes": [scope.value for scope in record.scopes],
                },
            )
        return event
