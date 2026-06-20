from __future__ import annotations

from fastapi import Depends, Request

from app.core.security import require_n8n_secret


def require_n8n_webhook_secret(request: Request) -> None:
    return require_n8n_secret(request)


N8nWebhookSecret = Depends(require_n8n_webhook_secret)
