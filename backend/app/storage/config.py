import os
from pathlib import Path
from urllib.parse import urlparse

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def _resolve_sqlite_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"sqlite", ""}:
        raise ValueError(f"Unsupported storage URL scheme: {parsed.scheme}")
    if parsed.path == ":memory:" or url == "sqlite:///:memory:":
        return ":memory:"
    if parsed.scheme == "sqlite":
        path = parsed.path or parsed.netloc
    else:
        path = url
    if path.startswith("/") and os.name == "nt":
        path = path[1:]
    path = path or "cyberalerta_guardian.db"
    p = Path(path)
    if not p.is_absolute():
        p = _PROJECT_ROOT / p
    return str(p)


class StorageConfig:
    storage_backend: str = os.getenv("STORAGE_BACKEND", "memory").strip().lower()
    sqlite_database_url: str = os.getenv("SQLITE_DATABASE_URL", "sqlite:///./cyberalerta_guardian.db").strip()

    def sqlite_path(self) -> str:
        return _resolve_sqlite_url(self.sqlite_database_url)


storage_config = StorageConfig()
