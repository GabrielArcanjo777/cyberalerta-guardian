import os
import secrets

from dotenv import load_dotenv

_env_loaded = False


def _ensure_env_loaded() -> None:
    global _env_loaded
    if _env_loaded:
        return
    # Tests (and any deterministic environment) can opt out of reading the local
    # .env so behavior does not depend on a developer's machine.
    if os.getenv("CYBERALERTA_DISABLE_DOTENV", "").strip().lower() in ("1", "true", "yes", "on"):
        _env_loaded = True
        return
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    env_path = os.path.join(project_root, ".env")
    if os.path.exists(env_path):
        app_env = os.getenv("APP_ENV", "development").strip().lower()
        load_dotenv(env_path, override=app_env in ("dev", "development", "local", "test"))
    _env_loaded = True


def _split_csv(value):
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def _env_int(name, default):
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


class AppConfig:
    def __init__(self):
        _ensure_env_loaded()
        self.app_env = os.getenv("APP_ENV", "development")
        self.dry_run = _env_bool("DRY_RUN", True)
        self.storage_backend = os.getenv("STORAGE_BACKEND", "memory").strip().lower()
        self.sqlite_database_url = os.getenv("SQLITE_DATABASE_URL", "sqlite:///./cyberalerta_guardian.db").strip()
        self.store_full_message = _env_bool("STORE_FULL_MESSAGE", False)
        self.risk_engine_version = os.getenv("RISK_ENGINE_VERSION", "v1")
        self.ruleset_version = os.getenv("RULESET_VERSION", "ruleset-local-v1")
        self.log_level = os.getenv("LOG_LEVEL", "INFO").strip().upper()
        self.enable_audit_log = _env_bool("ENABLE_AUDIT_LOG", True)
        self.api_key_enabled = _env_bool("API_KEY_ENABLED", False)
        self.api_key_header = os.getenv("API_KEY_HEADER", "X-CyberAlerta-API-Key")
        self.cyberalerta_api_key = os.getenv("CYBERALERTA_API_KEY", "")
        self.allowed_origins = self._safe_allowed_origins(_split_csv(os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")))
        self.frontend_base_url = os.getenv("FRONTEND_BASE_URL", "http://localhost:3000").strip().rstrip("/")
        self.n8n_allowed_origins = self._safe_allowed_origins(_split_csv(os.getenv("N8N_ALLOWED_ORIGINS", "http://localhost:5678")))
        self.n8n_webhook_secret = os.getenv("N8N_WEBHOOK_SECRET", "")
        self.n8n_webhook_header = os.getenv("N8N_WEBHOOK_HEADER", "X-N8N-CyberAlerta-Secret")
        self.n8n_base_url = os.getenv("N8N_BASE_URL", "")
        self.n8n_dry_run = _env_bool("N8N_DRY_RUN", True)
        self.trusted_webhook_ips = _split_csv(os.getenv("TRUSTED_WEBHOOK_IPS", ""))
        self.max_message_length = _env_int("MAX_MESSAGE_LENGTH", 4000)
        self.rate_limit_enabled = _env_bool("RATE_LIMIT_ENABLED", False)
        self.rate_limit_per_minute = max(1, _env_int("RATE_LIMIT_PER_MINUTE", 60))
        self.evolution_webhook_secret = os.getenv("EVOLUTION_WEBHOOK_SECRET", "")
        # Single trusted contact the bot may ever message. Canonical env is
        # TRUSTED_CONTACT; the two legacy per-channel vars are accepted as
        # fallbacks so existing .env files keep working.
        self.trusted_contact = (
            os.getenv("TRUSTED_CONTACT")
            or os.getenv("EVOLUTION_GUARDIAN_TO")
            or os.getenv("DUAL_BOT_GUARDIAN_TO")
            or ""
        ).strip()
        self.channel_provider = os.getenv("CHANNEL_PROVIDER", "evolution")
        self.dual_bot_channel_provider = os.getenv("DUAL_BOT_CHANNEL_PROVIDER", "mock_whatsapp")
        self.beta_real_send_enabled = _env_bool("BETA_REAL_SEND_ENABLED", False)
        self.beta_allowed_recipients = _split_csv(os.getenv("BETA_ALLOWED_RECIPIENTS", ""))
        self.beta_require_allowed_recipient = _env_bool("BETA_REQUIRE_ALLOWED_RECIPIENT", True)
        _auth_secret_key = os.getenv("AUTH_SECRET_KEY")
        if not _auth_secret_key:
            if self.is_production:
                raise RuntimeError(
                    "AUTH_SECRET_KEY must be set in production. Refusing to auto-generate a "
                    "per-process key (it would invalidate sessions across workers/restarts)."
                )
            _auth_secret_key = secrets.token_urlsafe(32)
        self.auth_secret_key = _auth_secret_key
        self.auth_access_token_expire_minutes = _env_int("AUTH_ACCESS_TOKEN_EXPIRE_MINUTES", 15)
        self.auth_refresh_token_expire_days = _env_int("AUTH_REFRESH_TOKEN_EXPIRE_DAYS", 7)
        self.auth_cookie_name = os.getenv("AUTH_COOKIE_NAME", "cyberalerta_session")
        self.auth_cookie_secure = _env_bool("AUTH_COOKIE_SECURE", self.is_production)
        self.auth_cookie_samesite = os.getenv("AUTH_COOKIE_SAMESITE", "lax").strip().lower()
        self.auth_rate_limit_enabled = _env_bool("AUTH_RATE_LIMIT_ENABLED", True)
        self.auth_require_sensitive_routes = _env_bool("AUTH_REQUIRE_SENSITIVE_ROUTES", False if self.is_development else True)
        self.google_oauth_enabled = _env_bool("GOOGLE_OAUTH_ENABLED", False)
        self.google_client_id = os.getenv("GOOGLE_CLIENT_ID", "")
        self.google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")
        self.google_redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
        self.google_auth_allowed_emails = _split_csv(os.getenv("GOOGLE_AUTH_ALLOWED_EMAILS", ""))
        self.google_auth_allowed_domains = _split_csv(os.getenv("GOOGLE_AUTH_ALLOWED_DOMAINS", ""))
        self.google_auto_create_users = _env_bool("GOOGLE_AUTO_CREATE_USERS", False)

    @property
    def is_development(self):
        return self.app_env.strip().lower() in ("dev", "development", "local", "test")

    @property
    def is_production(self):
        return self.app_env.strip().lower() in ("prod", "production")

    def _safe_allowed_origins(self, origins):
        if self.is_production:
            return [o for o in origins if o != "*"]
        return origins

    @property
    def cors_allowed_origins(self):
        seen = set()
        result = []
        for origin in self.allowed_origins + self.n8n_allowed_origins:
            if origin not in seen:
                seen.add(origin)
                result.append(origin)
        return result


config = AppConfig()
