import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from .config import config
from .request_context import set_request_id, set_n8n_execution_id


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        # Clickjacking + base-uri lockdown. Kept minimal so Swagger UI at /docs
        # (which loads its own scripts/styles) keeps working.
        response.headers["Content-Security-Policy"] = "frame-ancestors 'none'; base-uri 'none'"
        # HSTS only when cookies are already Secure (i.e. HTTPS/production).
        if config.auth_cookie_secure:
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
        return response


class RequestContextHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        set_request_id(request, request_id)

        n8n_execution_id = request.headers.get("X-N8N-Execution-ID")
        if n8n_execution_id:
            set_n8n_execution_id(request, n8n_execution_id)

        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
