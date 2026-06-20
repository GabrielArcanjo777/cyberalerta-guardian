# n8n Integration

## Overview

The CyberAlerta Guardian backend exposes n8n integration endpoints for real WhatsApp beta flows. The backend **never sends WhatsApp directly** — it only analyzes, decides, and returns structured responses. The n8n workflow is responsible for actual message delivery.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/integrations/n8n/health` | Health check, returns beta mode status |
| POST | `/integrations/n8n/whatsapp/inbound` | Analyze inbound WhatsApp message |
| POST | `/integrations/n8n/recovery` | Generate recovery playbook |
| POST | `/integrations/n8n/guardian-feedback` | Record guardian feedback |

## Authentication

All inbound endpoints (except health) require the n8n webhook secret header:

```
X-N8N-CyberAlerta-Secret: <N8N_WEBHOOK_SECRET>
```

Configure in `.env`:
```env
N8N_WEBHOOK_SECRET=your-secret-here
N8N_WEBHOOK_HEADER=X-N8N-CyberAlerta-Secret
```

In development mode (`APP_ENV=development`), if `N8N_WEBHOOK_SECRET` is empty, requests are allowed with a warning log.

## Beta Real Send Allowlist

To enable real WhatsApp message delivery through n8n:

```env
BETA_REAL_SEND_ENABLED=true
BETA_ALLOWED_RECIPIENTS=+5500000000000
BETA_REQUIRE_ALLOWED_RECIPIENT=true
```

### send_mode values

| Value | Condition |
|-------|-----------|
| `dry_run` | `BETA_REAL_SEND_ENABLED=false` (default) |
| `real_beta_allowed` | `BETA_REAL_SEND_ENABLED=true` AND recipient in allowlist |
| `real_beta_blocked` | `BETA_REAL_SEND_ENABLED=true` AND recipient NOT in allowlist |

**IMPORTANT**: Only real phone numbers in `BETA_ALLOWED_RECIPIENTS` will get `safe_to_send=true`. Never commit real numbers to GitHub.
