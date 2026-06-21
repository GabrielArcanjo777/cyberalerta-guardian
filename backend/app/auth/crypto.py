from __future__ import annotations

import base64
import hashlib
import hmac as hmac_mod
import json
import secrets
import struct
import time
from datetime import datetime, timedelta, timezone
from io import BytesIO
from typing import Any
from urllib.parse import quote

try:
    from argon2 import PasswordHasher as _Argon2Hasher
    from argon2.exceptions import VerifyMismatchError as _Argon2Mismatch
except ImportError:
    _Argon2Hasher = None  # type: ignore[assignment]
    _Argon2Mismatch = None  # type: ignore[assignment]

try:
    import qrcode
    from qrcode.image.svg import SvgPathImage
except ImportError:
    qrcode = None
    SvgPathImage = None

PASSWORD_SCHEME = "pbkdf2-sha256"
ARGON2_SCHEME = "argon2id"
PASSWORD_ITERATIONS = 600_000
TOTP_PERIOD_SECONDS = 30
TOTP_DIGITS = 6


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def normalize_email(email: str) -> str:
    return str(email or "").strip().lower()


def hash_password(password: str) -> str:
    if _Argon2Hasher is not None:
        hasher = _Argon2Hasher(time_cost=3, memory_cost=65536, parallelism=1, hash_len=32, salt_len=16)
        raw = hasher.hash(password)
        return f"{ARGON2_SCHEME}${raw}"
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS)
    return "$".join(
        [
            PASSWORD_SCHEME,
            str(PASSWORD_ITERATIONS),
            _b64url_encode(salt),
            _b64url_encode(digest),
        ]
    )


def verify_password(password: str, stored_hash: str | None) -> bool:
    if not password or not stored_hash:
        return False
    if stored_hash.startswith(f"{ARGON2_SCHEME}$"):
        if _Argon2Hasher is None or _Argon2Mismatch is None:
            return False
        raw = stored_hash[len(ARGON2_SCHEME) + 1:]
        try:
            return _Argon2Hasher().verify(raw, password)
        except _Argon2Mismatch:
            return False
        except Exception:
            return False
    try:
        scheme, iterations_raw, salt_raw, digest_raw = stored_hash.split("$", 3)
        if scheme != PASSWORD_SCHEME:
            return False
        iterations = int(iterations_raw)
        salt = _b64url_decode(salt_raw)
        expected = _b64url_decode(digest_raw)
    except (ValueError, TypeError):
        return False
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac_mod.compare_digest(actual, expected)


def validate_password_strength(password: str) -> list[str]:
    errors: list[str] = []
    if len(password or "") < 12:
        errors.append("Password must have at least 12 characters.")
    if not any(item.isupper() for item in password):
        errors.append("Password must include an uppercase letter.")
    if not any(item.islower() for item in password):
        errors.append("Password must include a lowercase letter.")
    if not any(item.isdigit() for item in password):
        errors.append("Password must include a number.")
    if not any(not item.isalnum() for item in password):
        errors.append("Password must include a symbol.")
    return errors


def sign_token(payload: dict[str, Any], secret: str, *, expires_in_seconds: int) -> str:
    now = datetime.now(timezone.utc)
    full_payload = {
        **payload,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=expires_in_seconds)).timestamp()),
        "jti": secrets.token_urlsafe(16),
    }
    body = _b64url_encode(json.dumps(full_payload, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    signature = _b64url_encode(hmac_mod.new(secret.encode("utf-8"), body.encode("ascii"), hashlib.sha256).digest())
    return f"{body}.{signature}"


def verify_token(token: str | None, secret: str, *, expected_type: str | None = None) -> dict[str, Any] | None:
    if not token or "." not in token:
        return None
    try:
        body, signature = token.split(".", 1)
        expected = _b64url_encode(hmac_mod.new(secret.encode("utf-8"), body.encode("ascii"), hashlib.sha256).digest())
        if not hmac_mod.compare_digest(signature, expected):
            return None
        payload = json.loads(_b64url_decode(body).decode("utf-8"))
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    if int(payload.get("exp", 0)) < int(time.time()):
        return None
    if expected_type and payload.get("type") != expected_type:
        return None
    return payload


def generate_totp_secret() -> str:
    return base64.b32encode(secrets.token_bytes(20)).decode("ascii").rstrip("=")


def _totp_code(secret: str, counter: int) -> str:
    padded = secret + "=" * (-len(secret) % 8)
    key = base64.b32decode(padded, casefold=True)
    message = struct.pack(">Q", counter)
    digest = hmac_mod.new(key, message, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    value = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return str(value % (10**TOTP_DIGITS)).zfill(TOTP_DIGITS)


def current_totp_code(secret: str, *, now: int | None = None) -> str:
    timestamp = int(time.time() if now is None else now)
    return _totp_code(secret, timestamp // TOTP_PERIOD_SECONDS)


def verify_totp(secret: str | None, code: str | None, *, window: int = 1) -> bool:
    if not secret or not code:
        return False
    normalized = str(code).strip()
    if not normalized.isdigit() or len(normalized) != TOTP_DIGITS:
        return False
    counter = int(time.time()) // TOTP_PERIOD_SECONDS
    for offset in range(-window, window + 1):
        if hmac_mod.compare_digest(_totp_code(secret, counter + offset), normalized):
            return True
    return False


def build_otpauth_uri(*, issuer: str, account_name: str, secret: str) -> str:
    label = quote(f"{issuer}:{account_name}")
    issuer_q = quote(issuer)
    return f"otpauth://totp/{label}?secret={secret}&issuer={issuer_q}&algorithm=SHA1&digits=6&period=30"


def build_qr_svg_base64(content: str) -> str:
    if qrcode is not None and SvgPathImage is not None:
        image = qrcode.make(content, image_factory=SvgPathImage)
        buffer = BytesIO()
        image.save(buffer)
        return base64.b64encode(buffer.getvalue()).decode("ascii")

    escaped = (
        content.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="320" height="320" viewBox="0 0 320 320">'
        '<rect width="320" height="320" fill="#ffffff"/>'
        '<rect x="28" y="28" width="72" height="72" fill="#0f172a"/>'
        '<rect x="220" y="28" width="72" height="72" fill="#0f172a"/>'
        '<rect x="28" y="220" width="72" height="72" fill="#0f172a"/>'
        '<text x="24" y="158" font-size="10" fill="#0f172a">Scan or enter the manual secret in your authenticator app.</text>'
        f'<text x="24" y="178" font-size="8" fill="#334155">{escaped[:180]}</text>'
        "</svg>"
    )
    return base64.b64encode(svg.encode("utf-8")).decode("ascii")


def generate_recovery_codes(count: int = 10) -> list[str]:
    codes: list[str] = []
    for _ in range(count):
        raw = secrets.token_hex(4).upper()
        codes.append(f"{raw[:4]}-{raw[4:]}")
    return codes


def hash_recovery_code(code: str) -> str:
    return hash_password(code)


def verify_recovery_code(code: str, code_hash: str) -> bool:
    return verify_password(code, code_hash)
