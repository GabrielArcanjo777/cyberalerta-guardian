import os
from typing import List


def _split_csv(value: str | None) -> List[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


class AppConfig:
    app_env: str = os.getenv("APP_ENV", "development")
    api_key_enabled: bool = os.getenv("API_KEY_ENABLED", "false").lower() == "true"
    api_key_header: str = os.getenv("API_KEY_HEADER", "X-CyberAlerta-API-Key")
    cyberalerta_api_key: str = os.getenv("CYBERALERTA_API_KEY", "")
    allowed_origins: List[str] = _split_csv(os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"))
    trusted_webhook_ips: List[str] = _split_csv(os.getenv("TRUSTED_WEBHOOK_IPS", ""))
    max_message_length: int = int(os.getenv("MAX_MESSAGE_LENGTH", "4000"))
    evolution_webhook_secret: str = os.getenv("EVOLUTION_WEBHOOK_SECRET", "")


config = AppConfig()
