from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from app.core.masking import mask_mapping

DEFAULT_LOGGER_NAME = "cyberalerta"


def get_logger(name: str | None = None) -> logging.Logger:
    if not name:
        return logging.getLogger(DEFAULT_LOGGER_NAME)
    if name.startswith(DEFAULT_LOGGER_NAME):
        return logging.getLogger(name)
    return logging.getLogger(f"{DEFAULT_LOGGER_NAME}.{name}")


def structured_log(
    logger: logging.Logger,
    event: str,
    *,
    level: int = logging.INFO,
    request_id: str | None = None,
    n8n_execution_id: str | None = None,
    **metadata: Any,
) -> None:
    payload: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
    }
    if request_id:
        payload["request_id"] = request_id
    if n8n_execution_id:
        payload["n8n_execution_id"] = n8n_execution_id
    if metadata:
        payload["metadata"] = mask_mapping(metadata)
    logger.log(level, json.dumps(payload, ensure_ascii=True, sort_keys=True, default=str))
