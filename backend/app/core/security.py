import hmac
import logging
import time
from threading import Lock

from fastapi import HTTPException, Request, status

from .config import config
from .logging import get_logger, structured_log
from .request_context import get_n8n_execution_id, get_request_id

logger = get_logger("security")

def require_api_key(request: Request) -> None:
    if not config.api_key_enabled:
        return None

    header_value = request.headers.get(config.api_key_header)
    if not header_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "APIKey"},
        )

    if not config.cyberalerta_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error",
        )

    if not hmac.compare_digest(header_value, config.cyberalerta_api_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )

    return None


def require_n8n_secret(request: Request) -> None:
    if not config.n8n_webhook_secret:
        if config.is_development:
            structured_log(
                logger,
                "webhook_allowed_without_secret",
                level=logging.WARNING,
                request_id=get_request_id(request),
                n8n_execution_id=get_n8n_execution_id(request),
                reason="development_n8n_secret_not_configured",
                header=config.n8n_webhook_header,
            )
            return None
        structured_log(
            logger,
            "webhook_rejected",
            level=logging.WARNING,
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
            level=logging.WARNING,
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
            level=logging.WARNING,
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


def validate_message_text(message: str | None, *, field_name: str = "message") -> str:
    normalized = str(message or "").strip()
    if not normalized:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"{field_name} cannot be empty.",
        )
    if len(normalized) > config.max_message_length:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"{field_name} exceeds max length of {config.max_message_length} characters.",
        )
    return normalized


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._requests: dict[str, list[float]] = {}
        self._lock = Lock()

    def check(self, key: str, *, limit: int, window_seconds: int = 60) -> bool:
        now = time.monotonic()
        cutoff = now - window_seconds
        with self._lock:
            hits = [hit for hit in self._requests.get(key, []) if hit >= cutoff]
            if len(hits) >= limit:
                self._requests[key] = hits
                return False
            hits.append(now)
            self._requests[key] = hits
            return True

    def reset(self) -> None:
        with self._lock:
            self._requests.clear()


rate_limiter = InMemoryRateLimiter()


def _client_identifier(request: Request) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",", 1)[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def check_rate_limit(request: Request, *, bucket: str) -> None:
    if not config.rate_limit_enabled:
        return None

    key = f"{bucket}:{_client_identifier(request)}"
    allowed = rate_limiter.check(key, limit=config.rate_limit_per_minute)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded.",
        )
    return None
