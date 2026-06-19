from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from app.event_model.models import new_id, utc_now


class OptInStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    REVOKED = "revoked"
    BOT_DISABLED = "bot_disabled"


class ConsentScope(str, Enum):
    PROTECTED_BOT = "protected_bot"
    RESPONSIBLE_ALERTS = "responsible_alerts"
    PATTERN_ANALYSIS = "pattern_analysis"
    CASE_HISTORY = "case_history"
    DEMO_CHANNEL = "demo_channel"


class ConsentEventType(str, Enum):
    ACCEPTED = "accepted"
    REVOKED = "revoked"
    BOT_ACTIVATED = "bot_activated"
    BOT_DEACTIVATED = "bot_deactivated"
    SCOPE_CHANGED = "scope_changed"


DEFAULT_CONSENT_SCOPES = [
    ConsentScope.PROTECTED_BOT,
    ConsentScope.RESPONSIBLE_ALERTS,
    ConsentScope.PATTERN_ANALYSIS,
    ConsentScope.CASE_HISTORY,
    ConsentScope.DEMO_CHANNEL,
]


class DataRetentionPolicy(BaseModel):
    policy_id: str = Field(default_factory=lambda: new_id("retention"))
    message_body_days: int = Field(default=90, ge=1)
    event_audit_days: int = Field(default=365, ge=1)
    delete_after_revocation_days: int = Field(default=30, ge=1)
    minimal_storage: bool = True
    policy_note: str = (
        "Retencao local minima para demonstracao; remocao fisica e automacoes legais "
        "ficam fora desta sprint."
    )


class ConsentRecord(BaseModel):
    consent_id: str = Field(default_factory=lambda: new_id("consent"))
    protected_person_id: str
    protected_person_alias: str = "Pessoa protegida"
    guardian_id: Optional[str] = None
    guardian_alias: Optional[str] = None
    channel_provider: str = "mock"
    status: OptInStatus = OptInStatus.PENDING
    scopes: List[ConsentScope] = Field(default_factory=list)
    bot_active: bool = False
    accepted_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    retention_policy: DataRetentionPolicy = Field(default_factory=DataRetentionPolicy)
    legal_basis: str = "consentimento"
    limitation_notice: str = (
        "Monitoramento somente com opt-in explicito. Ambiente local/demo, sem WhatsApp producao."
    )


class ConsentEvent(BaseModel):
    consent_event_id: str = Field(default_factory=lambda: new_id("consent-event"))
    consent_id: str
    event_type: ConsentEventType
    actor: str = "guardian_console"
    scopes: List[ConsentScope] = Field(default_factory=list)
    reason: Optional[str] = None
    occurred_at: datetime = Field(default_factory=utc_now)


class ConsentAcceptRequest(BaseModel):
    protected_person_id: str = "demo-protected-person"
    protected_person_alias: str = "Dona Lucia"
    guardian_id: Optional[str] = None
    guardian_alias: Optional[str] = "Gabriel"
    channel_provider: str = "mock"
    scopes: Optional[List[ConsentScope]] = None
    actor: str = "guardian_console"
    reason: Optional[str] = "Opt-in explicito registrado no Console."


class ConsentRevokeRequest(BaseModel):
    protected_person_id: str = "demo-protected-person"
    actor: str = "guardian_console"
    reason: Optional[str] = "Consentimento revogado pelo responsavel."


class ConsentBotActivationRequest(BaseModel):
    protected_person_id: str = "demo-protected-person"
    actor: str = "guardian_console"
    reason: Optional[str] = None


class ConsentScopeUpdateRequest(BaseModel):
    protected_person_id: str = "demo-protected-person"
    scopes: List[ConsentScope]
    actor: str = "guardian_console"
    reason: Optional[str] = "Escopos de consentimento atualizados."


class ConsentStatusResponse(BaseModel):
    record: ConsentRecord
    latest_event: Optional[ConsentEvent] = None
    events: List[ConsentEvent] = Field(default_factory=list)
    can_activate_bot: bool
    production_whatsapp_enabled: bool = False
    demo_notice: str = (
        "Consentimento local para demonstracao. Nao representa WhatsApp producao nem orientacao juridica."
    )
