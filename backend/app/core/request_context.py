from __future__ import annotations

import re
from dataclasses import dataclass
from uuid import uuid4

from fastapi import Request

REQUEST_ID_HEADER = "X-Request-ID"
N8N_EXECUTION_ID_HEADER = "X-N8N-Execution-ID"
_SAFE_HEADER_VALUE_RE = re.compile(r"[^A-Za-z0-9_.:/@-]")


@dataclass(frozen=True)
class RequestContext:
    request_id: str
    n8n_execution_id: str | None = None


def _safe_header_value(value: str | None, *, max_length: int = 180) -> str | None:
    normalized = str(value or "").strip()
    if not normalized:
        return None
    return _SAFE_HEADER_VALUE_RE.sub("-", normalized)[:max_length]


def build_request_id(value: str | None = None) -> str:
    return _safe_header_value(value) or f"req-{uuid4().hex}"


def build_n8n_execution_id(value: str | None = None) -> str | None:
    return _safe_header_value(value)


def attach_request_context(request: Request) -> RequestContext:
    context = RequestContext(
        request_id=build_request_id(request.headers.get(REQUEST_ID_HEADER)),
        n8n_execution_id=build_n8n_execution_id(request.headers.get(N8N_EXECUTION_ID_HEADER)),
    )
    request.state.request_id = context.request_id
    request.state.n8n_execution_id = context.n8n_execution_id
    return context


def get_request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None) or build_request_id(request.headers.get(REQUEST_ID_HEADER))


def get_n8n_execution_id(request: Request) -> str | None:
    return getattr(request.state, "n8n_execution_id", None) or build_n8n_execution_id(
        request.headers.get(N8N_EXECUTION_ID_HEADER)
    )
