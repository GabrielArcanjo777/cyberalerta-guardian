import os
from typing import List


def _split_csv(value: str | None) -> List[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


class AppConfig:
    def __init__(self) -> None:
        self.app_env: str = os.getenv("APP_ENV", "development")
        self.dry_run: bool = _env_bool("DRY_RUN", True)
        self.storage_backend: str = os.getenv("STORAGE_BACKEND", "memory").strip().lower()
        self.sqlite_database_url: str = os.getenv("SQLITE_DATABASE_URL", "sqlite:///./cyberalerta_guardian.db").strip()
        self.store_full_message: bool = _env_bool("STORE_FULL_MESSAGE", False)
        self.risk_engine_version: str = os.getenv("RISK_ENGINE_VERSION", "v1")
        self.ruleset_version: str = os.getenv("RULESET_VERSION", "ruleset-local-v1")
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO").strip().upper()
        self.enable_audit_log: bool = _env_bool("ENABLE_AUDIT_LOG", True)

        # API Key
        self.api_key_enabled: bool = _env_bool("API_KEY_ENABLED", False)
        self.api_key_header: str = os.getenv("API_KEY_HEADER", "X-CyberAlerta-API-Key")
        self.cyberalerta_api_key: str = os.getenv("CYBERALERTA_API_KEY", "")

        # CORS and origins
        self.allowed_origins: List[str] = self._safe_allowed_origins(
            _split_csv(os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"))
        )
        self.n8n_allowed_origins: List[str] = self._safe_allowed_origins(
            _split_csv(os.getenv("N8N_ALLOWED_ORIGINS", "http://localhost:5678"))
        )

        # n8n webhook security
        self.n8n_webhook_secret: str = os.getenv("N8N_WEBHOOK_SECRET", "")
        self.n8n_webhook_header: str = os.getenv("N8N_WEBHOOK_HEADER", "X-N8N-CyberAlerta-Secret")
        self.n8n_base_url: str = os.getenv("N8N_BASE_URL", "")
        self.n8n_dry_run: bool = _env_bool("N8N_DRY_RUN", True)

        # Rate limiting
        self.trusted_webhook_ips: List[str] = _split_csv(os.getenv("TRUSTED_WEBHOOK_IPS", ""))
        self.max_message_length: int = _env_int("MAX_MESSAGE_LENGTH", 4000)
        self.rate_limit_enabled: bool = _env_bool("RATE_LIMIT_ENABLED", False)
        self.rate_limit_per_minute: int = max(1, _env_int("RATE_LIMIT_PER_MINUTE", 60))

        # Evolution demo
        self.evolution_webhook_secret: str = os.getenv("EVOLUTION_WEBHOOK_SECRET", "")

        # Twilio
        self.channel_provider: str = os.getenv("CHANNEL_PROVIDER", "twilio_sandbox")
        self.dual_bot_channel_provider: str = os.getenv("DUAL_BOT_CHANNEL_PROVIDER", "mock_whatsapp")
        self.twilio_account_sid: str = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.twilio_auth_token: str = os.getenv("TWILIO_AUTH_TOKEN", "")
        self.twilio_whatsapp_from: str = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+1XXXXXXXXXX")
        self.twilio_webhook_secret: str = os.getenv("TWILIO_WEBHOOK_SECRET", "")
        self.twilio_validate_signature: bool = _env_bool("TWILIO_VALIDATE_SIGNATURE", False)
        self.twilio_guardian_to: str = os.getenv("TWILIO_GUARDIAN_TO", "")

        # LLM
        self.use_llm: bool = _env_bool("USE_LLM", False)
        self.llm_provider: str = os.getenv("LLM_PROVIDER", "mock")

        # --- Beta real controlado ---
        self.beta_real_send_enabled: bool = _env_bool("BETA_REAL_SEND_ENABLED", False)
        self.beta_allowed_recipients: List[str] = _split_csv(os.getenv("BETA_ALLOWED_RECIPIENTS", ""))
        self.beta_require_allowed_recipient: bool = _env_bool("BETA_REQUIRE_ALLOWED_RECIPIENT", True)

    @property
    def is_development(self) -> bool:
        return self.app_env.strip().lower() in {"dev", "development", "local", "test"}

    @property
    def is_production(self) -> bool:
        return self.app_env.strip().lower() in {"prod", "production"}

    def _safe_allowed_origins(self, origins: List[str]) -> List[str]:
        if self.is_production:
            return [origin for origin in origins if origin != "*"]
        return origins

    @property
    def cors_allowed_origins(self) -> List[str]:
        seen: set[str] = set()
        origins: List[str] = []
        for origin in [*self.allowed_origins, *self.n8n_allowed_origins]:
            if origin not in seen:
                seen.add(origin)
                origins.append(origin)
        return origins


config = AppConfig()
