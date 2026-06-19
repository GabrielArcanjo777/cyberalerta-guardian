import os
from urllib.parse import urlparse


class StorageConfig:
    storage_backend: str = os.getenv("STORAGE_BACKEND", "memory").strip().lower()
    sqlite_database_url: str = os.getenv("SQLITE_DATABASE_URL", "sqlite:///./cyberalerta_guardian.db").strip()

    def sqlite_path(self) -> str:
        parsed = urlparse(self.sqlite_database_url)
        if parsed.scheme not in {"sqlite", ""}:
            raise ValueError(f"Unsupported storage URL scheme: {parsed.scheme}")
        if parsed.path == ":memory:" or self.sqlite_database_url == "sqlite:///:memory:":
            return ":memory:"
        if parsed.scheme == "sqlite":
            path = parsed.path or parsed.netloc
        else:
            path = self.sqlite_database_url
        if path.startswith("/") and os.name == "nt":
            path = path[1:]
        return path


storage_config = StorageConfig()
