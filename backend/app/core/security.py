import hmac
from fastapi import Depends, HTTPException, Request, status
from .config import config


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
