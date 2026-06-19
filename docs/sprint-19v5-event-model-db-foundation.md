# Sprint 19V5 - Event Model + Database Foundation

## Scope

This sprint strengthens the provider-neutral domain foundation before any V5 channel adapter is implemented.

Implemented:

- Minimum entities: `User`, `ProtectedPerson`, `Guardian`, `Case`, `Message`, `BotEvent`, `RiskAssessment`, `ChannelConnection`, `AuditLog`.
- Repository protocols and in-memory repositories for all minimum entities.
- Event metadata for auditability: `source`, `actor`, `case_id`, `protected_person_id`.
- Audit log recording for events published through `LocalEventBus` when an audit repository is provided.
- Initial rule-based risk assessment with explainable signals and score capped at `0-100`.
- Canonical V5 events: `ResponsibleAlertQueued`, `ResponsibleNotified`, `PatternCandidateDetected`.

## Initial Risk Signals

- `urgency`
- `pix_or_payment`
- `new_number`
- `unknown_link`
- `do_not_call`
- `secrecy_request`
- `emotional_pressure`
- `password_or_code`

## Adapter-First Boundary

The core stores internal messages, cases, assessments, events and channel connection metadata. External providers should normalize payloads before calling the core. Raw provider payloads, secrets and provider-specific behavior stay outside the Event Model.

This prepares Sprint 20V5 by giving the future Channel Adapter Contract stable internal entities and repositories to target.

## Out of Scope

- Evolution API.
- Twilio implementation changes.
- Meta Cloud API.
- WhatsApp production.
- Advanced agents.
- Advanced Pattern Intelligence.
- Front premium changes.
