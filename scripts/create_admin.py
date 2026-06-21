from __future__ import annotations

import getpass
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.auth.crypto import hash_password, validate_password_strength  # noqa: E402
from app.auth.models import UserRole  # noqa: E402
from app.auth.repository import get_auth_repository  # noqa: E402
from app.auth.service import AuthService  # noqa: E402
from app.core.config import config  # noqa: E402


def _prompt(label: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{label}{suffix}: ").strip()
    return value or (default or "")


def _password_from_env() -> str | None:
    if not config.is_development:
        return None
    return os.getenv("INITIAL_ADMIN_PASSWORD")


def main() -> int:
    repository = get_auth_repository()
    service = AuthService(repository)

    email = os.getenv("INITIAL_ADMIN_EMAIL") if config.is_development else None
    name = os.getenv("INITIAL_ADMIN_NAME") if config.is_development else None
    password = _password_from_env()

    email = (email or _prompt("Admin email")).strip().lower()
    name = (name or _prompt("Admin name", "CyberAlerta Admin")).strip()

    existing = repository.get_user_by_email(email)
    if existing:
        print("Admin user already exists for this email.")
        confirmation = input("Type OVERWRITE to replace password/role, or press Enter to abort: ").strip()
        if confirmation != "OVERWRITE":
            print("Aborted.")
            return 1

    if not password:
        password = getpass.getpass("Admin password: ")
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("Passwords do not match.")
            return 1

    errors = validate_password_strength(password)
    if errors:
        print("Password is not strong enough:")
        for error in errors:
            print(f"- {error}")
        return 1

    if existing:
        updated = existing.model_copy(
            update={
                "password_hash": hash_password(password),
                "full_name": name,
                "role": UserRole.ADMIN,
                "is_admin": True,
                "is_active": True,
            }
        )
        repository.update_user(updated)
        print("Admin user updated.")
        return 0

    service.create_user(email=email, full_name=name, password=password, role=UserRole.ADMIN, is_admin=True)
    print("Admin user created.")
    if config.storage_backend != "sqlite":
        print("Warning: STORAGE_BACKEND is not sqlite; this admin exists only in the current in-memory runtime.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
