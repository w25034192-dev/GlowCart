from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import threading
import uuid
from typing import Any

import bcrypt
import jwt

from app.core.config import get_settings

try:
    from argon2 import PasswordHasher
    from argon2.exceptions import VerifyMismatchError

    _ARGON2_HASHER: PasswordHasher | None = PasswordHasher()
except ImportError:  # pragma: no cover - fallback when argon2-cffi binary is unavailable
    _ARGON2_HASHER = None
    VerifyMismatchError = Exception  # type: ignore[misc, assignment]


_REVOKED_JTI_LOCK = threading.Lock()
_REVOKED_JTIS: set[str] = set()


def hash_password(password: str) -> str:
    """Hash a password with Argon2id when available, else bcrypt."""
    if _ARGON2_HASHER is not None:
        return _ARGON2_HASHER.hash(password)
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify a password against an Argon2id or bcrypt hash."""
    if password_hash.startswith("$argon2"):
        if _ARGON2_HASHER is None:
            return False
        try:
            return _ARGON2_HASHER.verify(password_hash, plain_password)
        except VerifyMismatchError:
            return False
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except ValueError:
        return False


def create_token(
    subject: str,
    role: str,
    token_type: str,
    expires_delta: timedelta,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "type": token_type,
        "jti": str(uuid.uuid4()),
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(user_id: str, role: str) -> str:
    settings = get_settings()
    return create_token(
        subject=user_id,
        role=role,
        token_type="access",
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )


def create_refresh_token(user_id: str, role: str) -> str:
    settings = get_settings()
    return create_token(
        subject=user_id,
        role=role,
        token_type="refresh",
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
    )


def decode_token(token: str, expected_type: str | None = None) -> dict[str, Any]:
    settings = get_settings()
    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )
    if expected_type and payload.get("type") != expected_type:
        raise jwt.InvalidTokenError("Invalid token type")
    jti = payload.get("jti")
    if jti and is_token_revoked(jti):
        raise jwt.InvalidTokenError("Token has been revoked")
    return payload


def revoke_token_jti(jti: str) -> None:
    with _REVOKED_JTI_LOCK:
        _REVOKED_JTIS.add(jti)


def is_token_revoked(jti: str) -> bool:
    with _REVOKED_JTI_LOCK:
        return jti in _REVOKED_JTIS


def reset_revoked_tokens() -> None:
    with _REVOKED_JTI_LOCK:
        _REVOKED_JTIS.clear()


def hash_token_sha256(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def sign_webhook_payload(raw_body: bytes, secret: str) -> str:
    return hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()


def verify_webhook_signature(raw_body: bytes, signature: str, secret: str) -> bool:
    expected = sign_webhook_payload(raw_body, secret)
    return hmac.compare_digest(expected, signature)

