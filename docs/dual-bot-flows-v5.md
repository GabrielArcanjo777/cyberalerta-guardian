# Sprint 23V5 - Dual Bot Flows

## Scope

Dual Bot is the assisted protection flow:

1. The protected person sends a message through a channel adapter.
2. The adapter normalizes the provider payload into `InboundMessage`.
3. Event Model records `MessageReceived` and `SuspiciousMessageReceived`.
4. Risk Assessment calculates explainable risk.
5. Case Management creates a case when threshold is reached.
6. Bot Protegido sends a short safe reply.
7. Bot Responsavel receives an alert with context.
8. Responsible feedback updates the case and records audit events.

## Provider Boundary

The flow uses `ChannelAdapter` and works with:

- `MockWhatsAppAdapter` for local simulation.
- `EvolutionDemoAdapter` for development/demo only.

Evolution API is not production and must not be described as official WhatsApp Business.

## Default Messages

Bot Protegido risk reply:

```text
Recebi sua mensagem. Ela tem sinais de risco. Nao faca pagamento nem clique em links por enquanto. Vou avisar seu contato de confianca.
```

Bot Responsavel alert:

```text
Alerta Guardian: {person} recebeu uma mensagem com sinais de golpe. Risco: {risk}. Sinais: {signals}. Caso {case_id}. Acesse o caso para revisar.
```

## Events

- `MessageReceived`
- `RiskAssessmentCreated`
- `CaseCreated`
- `SafeReplySent`
- `ResponsibleAlertQueued`
- `ResponsibleNotified`
- `GuardianFeedbackReceived`
- `CaseResolved`
- `FalsePositiveMarked`

Compatibility events like `SuspiciousMessageReceived` and `ProtectedPersonReplied` are still emitted where existing flows consume them.

## Configuration

```env
DUAL_BOT_CHANNEL_PROVIDER=mock_whatsapp
DUAL_BOT_GUARDIAN_TO=
```

For Evolution demo mode:

```env
DUAL_BOT_CHANNEL_PROVIDER=evolution_demo
EVOLUTION_API_URL=
EVOLUTION_API_KEY=
EVOLUTION_INSTANCE_NAME=
EVOLUTION_GUARDIAN_TO=
```

Production WhatsApp should be implemented later through `MetaCloudApiAdapter` behind the same contract.
