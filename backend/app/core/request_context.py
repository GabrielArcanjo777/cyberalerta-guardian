from starlette.requests import Request

_REQUEST_ID_ATTR = "_cyberalerta_request_id"
_N8N_EXECUTION_ID_ATTR = "_cyberalerta_n8n_execution_id"


def get_request_id(request: Request) -> str | None:
    return getattr(request.state, _REQUEST_ID_ATTR, None) or request.headers.get("X-Request-ID")


def set_request_id(request: Request, value: str) -> None:
    setattr(request.state, _REQUEST_ID_ATTR, value)


def get_n8n_execution_id(request: Request) -> str | None:
    return getattr(request.state, _N8N_EXECUTION_ID_ATTR, None) or request.headers.get("X-N8N-Execution-ID")


def set_n8n_execution_id(request: Request, value: str) -> None:
    setattr(request.state, _N8N_EXECUTION_ID_ATTR, value)
