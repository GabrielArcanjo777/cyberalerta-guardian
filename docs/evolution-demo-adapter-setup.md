# Evolution Demo Adapter - Local Setup

EvolutionDemoAdapter is a development and technical demo provider. It is not an official WhatsApp Business production integration.

Production readiness should use `MetaCloudApiAdapter` or another official provider behind the same `ChannelAdapter` contract.

## Environment

Set these values in `.env`:

```env
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=
EVOLUTION_INSTANCE_NAME=guardian-demo
```

Keep the local demo key only in your uncommitted `.env`.

Optional, for sending a demo alert to a responsible contact through the same Evolution instance:

```env
EVOLUTION_GUARDIAN_TO=5511999990001
```

Do not commit real keys, tokens or phone numbers.

## Docker

Example local-only `docker-compose.yml`:

```yaml
services:
  evolution-api:
    image: atendai/evolution-api:latest
    ports:
      - "8080:8080"
    environment:
      AUTHENTICATION_API_KEY: "replace-with-local-demo-key"
      SERVER_URL: "http://localhost:8080"
```

Start it:

```bash
docker compose up -d
```

## Create Instance And QR Code

Use the Evolution API local dashboard or API endpoints to:

1. Create an instance named like `EVOLUTION_INSTANCE_NAME`.
2. Connect the instance with QR Code.
3. Confirm the instance is connected before testing webhooks.

Exact Evolution API routes can vary by version, so keep this repo isolated from those details. Only `EvolutionDemoAdapter` should know the provider-specific shape.

## Webhook

Local backend endpoint:

```text
POST http://localhost:8000/webhook/evolution
```

Health endpoint:

```text
GET http://localhost:8000/webhook/evolution/health
```

Configure Evolution webhook for `MESSAGES_UPSERT` events pointing to the backend URL.

## Ngrok

If Evolution runs outside the same local network, expose the backend:

```bash
ngrok http 8000
```

Then configure the Evolution webhook URL:

```text
https://your-ngrok-subdomain.ngrok-free.app/webhook/evolution
```

## Local Payload Test

```bash
curl -X POST http://localhost:8000/webhook/evolution \
  -H "Content-Type: application/json" \
  -d '{
    "event": "MESSAGES_UPSERT",
    "instance": "guardian-demo",
    "data": {
      "key": {
        "id": "EVODEMO001",
        "remoteJid": "5511999990001@s.whatsapp.net",
        "fromMe": false
      },
      "pushName": "Dona Lucia",
      "messageTimestamp": 1780000000,
      "message": {
        "conversation": "Mae, troquei de numero. Preciso de um Pix urgente. Nao liga agora."
      }
    }
  }'
```

Expected flow:

1. `EvolutionDemoAdapter` parses `MESSAGES_UPSERT`.
2. Payload becomes provider-neutral `InboundMessage`.
3. `ChannelIngressService` routes it into Event Model.
4. Risk Assessment runs.
5. Case Management creates a case if threshold is reached.
6. A safe reply is sent through Evolution if env vars are configured.
7. Responsible alert is sent to `EVOLUTION_GUARDIAN_TO` if configured, otherwise simulated for demo audit.

## Future Meta Cloud API Swap

To move toward production, implement `MetaCloudApiAdapter` with the same `ChannelAdapter` methods:

- `parseProviderPayload`
- `sendMessage`
- `mapDeliveryStatus`
- `validateConnection`
- `getProviderName`

The core should remain unchanged because it only receives `InboundMessage`, `OutboundMessage` and `DeliveryStatusEvent`.
