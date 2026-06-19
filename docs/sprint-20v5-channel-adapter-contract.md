# Sprint 20V5 - Channel Adapter Contract

## Scope

This sprint defines the provider-neutral channel contract. The core must receive normalized internal messages and must not depend on Evolution API, Twilio, Meta Cloud API or any other provider payload.

Implemented:

- `ChannelAdapter` protocol.
- `ChannelProvider` enum with `MOCK_WHATSAPP`, `EVOLUTION_DEMO`, `TWILIO_SANDBOX`, `META_CLOUD_API`.
- `InboundMessage` normalized type.
- `OutboundMessage` normalized type.
- `DeliveryStatusEvent` for provider delivery callbacks.
- `ChannelConnectionValidation`.
- Internal helpers for normalization, inbound receiving, outbound sending and delivery status mapping.
- `ChannelIngressService.ingest_normalized` so application/core code can route normalized messages without reading provider payloads.
- Minimal channel audit log entries through the Event Model `AuditLog` repository.

## Adapter-First Boundary

Providers parse their raw payloads inside adapters. After parsing, the application receives only `InboundMessage`. Outbound requests are expressed as `OutboundMessage`. Delivery callbacks are mapped to `DeliveryStatusEvent`.

This keeps Case Management, Risk Assessment, Dual Bot flows and Console logic independent from provider-specific SDKs, field names or webhook shapes.

## Prepared Future Adapters

- `MockWhatsAppAdapter` can implement `ChannelAdapter` and emit local `InboundMessage`/`OutboundMessage` without changing the core.
- `EvolutionDemoAdapter` can parse Evolution payloads internally and expose only normalized messages, while remaining clearly demo-only.
- `TwilioSandboxAdapter` and `MetaCloudApiAdapter` can be added later behind the same contract.

## Out of Scope

- Evolution API implementation.
- Twilio implementation changes.
- Meta Cloud API.
- WhatsApp production.
- Mock WhatsApp Sprint 21V5 implementation.
- Webhook routes for real providers.
- Front premium changes.
