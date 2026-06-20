# Sprint 22V4 - Twilio Sandbox Adapter

## Objetivo

O `TwilioSandboxWhatsAppAdapter` valida o fluxo real de WhatsApp em ambiente controlado.
Ele nao e producao e nao substitui WhatsApp Business definitivo.

O core continua desacoplado: webhooks Twilio entram pelo adapter, viram
`NormalizedInboundMessage`, passam pelo `ChannelIngressService` e seguem para o Event Model.

## Endpoints

- `GET /api/channels/twilio/whatsapp/health`
- `POST /api/channels/twilio/whatsapp/inbound`
- `POST /api/channels/twilio/whatsapp/status`

## Variaveis de ambiente

```env
CHANNEL_PROVIDER=twilio_sandbox
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_WHATSAPP_FROM=whatsapp:+1XXXXXXXXXX
TWILIO_WEBHOOK_SECRET=
TWILIO_STATUS_CALLBACK_URL=
TWILIO_GUARDIAN_TO=
TWILIO_VALIDATE_SIGNATURE=false
```

Nao commitar `.env`, tokens, Account SID, Auth Token ou numeros reais.

## Setup local

1. Configure `.env` local com as credenciais do Twilio Sandbox.
2. Suba o backend local.
3. Exponha o backend com um tunnel local, por exemplo ngrok.
4. Configure no Twilio Sandbox:
   - inbound: `POST https://seu-tunnel/api/channels/twilio/whatsapp/inbound`
   - status callback: `POST https://seu-tunnel/api/channels/twilio/whatsapp/status`
5. Configure `TWILIO_STATUS_CALLBACK_URL` com a URL publica do status callback.
6. Configure `TWILIO_GUARDIAN_TO` com o numero WhatsApp do responsavel do piloto.

## Assinatura

`TWILIO_VALIDATE_SIGNATURE=false` facilita testes locais.

Para validar assinatura no piloto:

- defina `TWILIO_VALIDATE_SIGNATURE=true`;
- use `TWILIO_WEBHOOK_SECRET` ou `TWILIO_AUTH_TOKEN`;
- garanta que a URL recebida pelo backend seja exatamente a URL publica configurada na Twilio.

## Comportamento esperado

Inbound suspeito:

1. Twilio envia `MessageSid`, `From`, `To`, `Body` e metadados.
2. Adapter normaliza para `NormalizedInboundMessage`.
3. Idempotencia usa `MessageSid`.
4. Event Model cria `SuspiciousMessageReceived` e `RiskAssessmentCreated`.
5. Se o score atingir o limite, cria `CaseCreated` e `GuardianAlertTriggered`.
6. Adapter tenta enviar resposta ao protegido e alerta ao responsavel.
7. Delivery e status callback geram `DeliveryStatusUpdated`.

## Fora do escopo

- WhatsApp producao.
- Meta Cloud API.
- Templates oficiais de producao.
- Console visual novo.
- Agentes avancados.
- Pattern Intelligence avancado.
