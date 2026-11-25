import uuid
import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_token
from app.db.session import get_db
from app.models import User
from app.repositories.user_repository import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_token_payload(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError("Missing or invalid Authorization header.")
    try:
        return decode_token(credentials.credentials, expected_type="access")
    except jwt.InvalidTokenError as exc:
        raise UnauthorizedError("Invalid or expired access token.") from exc


def get_current_user(
    payload: dict = Depends(get_current_token_payload),
    db: Session = Depends(get_db),
) -> User:
    try:
        user_id = uuid.UUID(payload["sub"])
    except (KeyError, ValueError) as exc:
        raise UnauthorizedError("Malformed token subject.") from exc

    user = UserRepository(db).get_by_id(user_id)
    if user is None or not user.is_active:
        raise UnauthorizedError("Authenticated user not found or inactive.")
    return user


def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User | None:
    if credentials is None:
        return None
    try:
        payload = decode_token(credentials.credentials, expected_type="access")
        user_id = uuid.UUID(payload["sub"])
        user = UserRepository(db).get_by_id(user_id)
        return user if user and user.is_active else None
    except (jwt.InvalidTokenError, ValueError, KeyError):
        return None


def require_roles(*allowed_roles: str):
    def _role_guard(user: User = Depends(get_current_user)) -> User:
        role_name = user.role.name if user.role else ""
        if role_name not in allowed_roles:
            raise ForbiddenError("You do not have permission to perform this action.")
        return user

    return _role_guard

