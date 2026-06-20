import logging
from typing import Any

_REQUEST_ID_KEY = "request_id"
_N8N_EXECUTION_ID_KEY = "n8n_execution_id"


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(f"cyberalerta.{name}")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s %(name)s %(message)s"))
        logger.addHandler(handler)
    return logger


def structured_log(
    logger: logging.Logger,
    event: str,
    *,
    level: int = logging.INFO,
    request_id: str | None = None,
    n8n_execution_id: str | None = None,
    **kwargs: Any,
) -> None:
    parts = [f"event={event}"]
    if request_id:
        parts.append(f"request_id={request_id}")
    if n8n_execution_id:
        parts.append(f"n8n_execution_id={n8n_execution_id}")
    for key, value in kwargs.items():
        parts.append(f"{key}={value}")
    logger.log(level, " ".join(parts))
