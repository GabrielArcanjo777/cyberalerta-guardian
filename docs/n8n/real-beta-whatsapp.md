# Real Beta WhatsApp Setup

## Prerequisites

1. n8n instance running (local or cloud)
2. WhatsApp Business Cloud API account OR Twilio WhatsApp sandbox
3. CyberAlerta Guardian backend running

## Local Setup

### 1. Configure Backend `.env`

```env
APP_ENV=development
DRY_RUN=true
BETA_REAL_SEND_ENABLED=false
BETA_ALLOWED_RECIPIENTS=
BETA_REQUIRE_ALLOWED_RECIPIENT=true
N8N_WEBHOOK_SECRET=change-me-in-production
```

### 2. Start Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 3. Verify Health

```bash
curl http://localhost:8000/integrations/n8n/health
```

Expected response:
```json
{
  "status": "ok",
  "integration": "n8n",
  "mode": "beta",
  "real_whatsapp_send_enabled": false
}
```

### 4. Test Inbound (Dry Run)

```bash
curl -X POST http://localhost:8000/integrations/n8n/whatsapp/inbound \
  -H "Content-Type: application/json" \
  -H "X-N8N-Execution-ID: teste-001" \
  -d '{
    "message_id": "msg-teste-001",
    "user_name": "Maria",
    "from_number": "+5500000000000",
    "reply_to_number": "+5500000000000",
    "message": "Mãe, troquei de número. Preciso de um Pix urgente agora.",
    "channel": "whatsapp",
    "action_type": "pix",
    "already_acted": false,
    "trusted_contact_name": "João",
    "trusted_contact_relation": "filho",
    "trusted_contact_phone": "+5500000000000"
  }'
```

Expected: `safe_to_send=false`, `send_mode=dry_run`

## Enabling Real Send (Beta)

### 1. Add Your Number to Allowlist

Edit your local `.env` (never commit this):

```env
BETA_REAL_SEND_ENABLED=true
BETA_ALLOWED_RECIPIENTS=+55SEU_NUMERO_AQUI
BETA_REQUIRE_ALLOWED_RECIPIENT=true
```

### 2. Restart Backend

```bash
uvicorn main:app --reload --port 8000
```

### 3. Verify Allowlist Works

```bash
curl -X POST http://localhost:8000/integrations/n8n/whatsapp/inbound \
  -H "Content-Type: application/json" \
  -d '{
    "message_id": "msg-beta-001",
    "user_name": "Maria",
    "reply_to_number": "+55SEU_NUMERO_AQUI",
    "message": "Pix urgente para conta nova.",
    "channel": "whatsapp"
  }'
```

Expected: `safe_to_send=true`, `send_mode=real_beta_allowed`

### 4. Configure n8n Workflow

See [whatsapp-flow.md](./whatsapp-flow.md) for the complete n8n workflow configuration.

## Security Rules

- Backend never sends WhatsApp directly
- n8n only sends when `safe_to_send=true` AND `send_mode=real_beta_allowed`
- Real numbers only in local `.env`, never in GitHub
- In production, `N8N_WEBHOOK_SECRET` is required
- Rate limiting can be enabled via `RATE_LIMIT_ENABLED=true`
