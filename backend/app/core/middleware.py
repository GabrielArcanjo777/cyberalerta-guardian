import logging
from time import perf_counter

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.logging import get_logger, structured_log
from app.core.request_context import (
    N8N_EXECUTION_ID_HEADER,
    REQUEST_ID_HEADER,
    attach_request_context,
)

logger = get_logger("http")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response


class RequestContextHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        context = attach_request_context(request)
        start = perf_counter()
        try:
            response: Response = await call_next(request)
        except Exception:
            structured_log(
                logger,
                "request_failed",
                level=logging.ERROR,
                request_id=context.request_id,
                n8n_execution_id=context.n8n_execution_id,
                method=request.method,
                path=request.url.path,
                duration_ms=round((perf_counter() - start) * 1000, 2),
            )
            raise

        response.headers[REQUEST_ID_HEADER] = context.request_id
        if context.n8n_execution_id:
            response.headers[N8N_EXECUTION_ID_HEADER] = context.n8n_execution_id

        structured_log(
            logger,
            "request_completed",
            request_id=context.request_id,
            n8n_execution_id=context.n8n_execution_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round((perf_counter() - start) * 1000, 2),
        )
        return response
