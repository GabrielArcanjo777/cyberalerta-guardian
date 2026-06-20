from __future__ import annotations

import hmac

from fastapi import Depends, HTTPException, Request, status

from app.core.logging import get_logger, structured_log
from app.core.config import config
from app.core.request_context import get_n8n_execution_id, get_request_id

logger = get_logger("n8n.security")


async def require_n8n_webhook_secret(request: Request) -> None:
    if not config.n8n_webhook_secret:
        if config.is_development:
            structured_log(
                logger,
                "webhook_allowed_without_secret",
                level=20,
                request_id=get_request_id(request),
                n8n_execution_id=get_n8n_execution_id(request),
                reason="development_n8n_secret_not_configured",
                header=config.n8n_webhook_header,
            )
            return None
        structured_log(
            logger,
            "webhook_rejected",
            level=40,
            request_id=get_request_id(request),
            n8n_execution_id=get_n8n_execution_id(request),
            reason="server_missing_n8n_secret",
            header=config.n8n_webhook_header,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error",
        )

    header_value = request.headers.get(config.n8n_webhook_header)
    if not header_value:
        structured_log(
            logger,
            "webhook_rejected",
            level=40,
            request_id=get_request_id(request),
            n8n_execution_id=get_n8n_execution_id(request),
            reason="missing_n8n_secret_header",
            header=config.n8n_webhook_header,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "APIKey"},
        )

    if not hmac.compare_digest(header_value, config.n8n_webhook_secret):
        structured_log(
            logger,
            "webhook_rejected",
            level=40,
            request_id=get_request_id(request),
            n8n_execution_id=get_n8n_execution_id(request),
            reason="invalid_n8n_secret",
            header=config.n8n_webhook_header,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )

    return None
