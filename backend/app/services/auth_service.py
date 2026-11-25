from datetime import datetime, timedelta, timezone
import secrets
import uuid
import jwt
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import BadRequestError, ConflictError, NotFoundError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token_sha256,
    revoke_token_jti,
    verify_password,
)
from app.models import Address, Cart, User, Wishlist
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    AddressCreate,
    AddressUpdate,
    AdminUserCreateRequest,
    LoginRequest,
    ProfileUpdateRequest,
    RegisterRequest,
    UserResponse,
)
from app.services.audit_service import record_audit_log


def serialize_user(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        role=user.role.name if user.role else "customer",
        is_active=user.is_active,
        created_at=user.created_at,
    )


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = UserRepository(db)

    def register(self, payload: RegisterRequest, ip_address: str | None = None) -> UserResponse:
        email = payload.email.lower().strip()
        if self.repo.get_by_email(email) is not None:
            raise ConflictError("An account with this email already exists.")

        roles = self.repo.ensure_default_roles()
        customer_role = roles["customer"]

        user = User(
            role_id=customer_role.id,
            email=email,
            full_name=payload.full_name.strip(),
            phone=payload.phone,
            password_hash=hash_password(payload.password),
            is_active=True,
        )
        self.db.add(user)
        self.db.flush()
        self.db.add(Cart(user_id=user.id))
        self.db.add(Wishlist(user_id=user.id))
        record_audit_log(
            self.db,
            actor_id=user.id,
            action="USER_REGISTERED",
            resource_type="user",
            resource_id=str(user.id),
            details={"email": email},
            ip_address=ip_address,
        )
        self.db.commit()
        user = self.repo.get_by_id(user.id)
        assert user is not None
        return serialize_user(user)

    def login(self, payload: LoginRequest, ip_address: str | None = None) -> dict:
        user = self.repo.get_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.password_hash):
            raise UnauthorizedError("Invalid email or password.")
        if not user.is_active:
            raise UnauthorizedError("Account is disabled.")

        role_name = user.role.name
        access_token = create_access_token(str(user.id), role_name)
        refresh_token = create_refresh_token(str(user.id), role_name)
        record_audit_log(
            self.db,
            actor_id=user.id,
            action="USER_LOGIN",
            resource_type="user",
            resource_id=str(user.id),
            ip_address=ip_address,
        )
        self.db.commit()
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": serialize_user(user),
        }

    def refresh(self, refresh_token: str) -> dict:
        try:
            payload = decode_token(refresh_token, expected_type="refresh")
        except jwt.InvalidTokenError as exc:
            raise UnauthorizedError("Invalid or expired refresh token.") from exc

        user_id = uuid.UUID(payload["sub"])
        user = self.repo.get_by_id(user_id)
        if user is None or not user.is_active:
            raise UnauthorizedError("Account unavailable.")

        if payload.get("jti"):
            revoke_token_jti(payload["jti"])

        role_name = user.role.name
        return {
            "access_token": create_access_token(str(user.id), role_name),
            "refresh_token": create_refresh_token(str(user.id), role_name),
            "token_type": "bearer",
            "user": serialize_user(user),
        }

    def logout(self, access_jti: str | None, refresh_token: str | None) -> None:
        if access_jti:
            revoke_token_jti(access_jti)
        if refresh_token:
            try:
                payload = decode_token(refresh_token, expected_type="refresh")
                if payload.get("jti"):
                    revoke_token_jti(payload["jti"])
            except jwt.InvalidTokenError:
                pass

    def forgot_password(self, email: str) -> dict:
        settings = get_settings()
        user = self.repo.get_by_email(email)
        if user is None:
            return {
                "message": "If an account exists for this email, a reset link has been generated.",
                "reset_token": None,
            }
        raw_token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.password_reset_token_expire_minutes
        )
        user.reset_token_hash = hash_token_sha256(raw_token)
        user.reset_token_expires_at = expires_at.isoformat()
        record_audit_log(
            self.db,
            actor_id=user.id,
            action="PASSWORD_RESET_REQUESTED",
            resource_type="user",
            resource_id=str(user.id),
        )
        self.db.commit()
        return {
            "message": "If an account exists for this email, a reset link has been generated.",
            "reset_token": raw_token if settings.app_env != "production" else None,
        }

    def reset_password(self, raw_token: str, new_password: str) -> None:
        token_hash = hash_token_sha256(raw_token)
        user = (
            self.db.query(User)
            .filter(User.reset_token_hash == token_hash)
            .first()
        )
        if user is None or not user.reset_token_expires_at:
            raise BadRequestError("Invalid or expired password reset token.")
        expires_at = datetime.fromisoformat(user.reset_token_expires_at)
        if expires_at < datetime.now(timezone.utc):
            raise BadRequestError("Password reset token has expired.")

        user.password_hash = hash_password(new_password)
        user.reset_token_hash = None
        user.reset_token_expires_at = None
        record_audit_log(
            self.db,
            actor_id=user.id,
            action="PASSWORD_RESET_COMPLETED",
            resource_type="user",
            resource_id=str(user.id),
        )
        self.db.commit()

    def update_profile(self, user: User, payload: ProfileUpdateRequest) -> UserResponse:
        if payload.full_name is not None:
            user.full_name = payload.full_name.strip()
        if payload.phone is not None:
            user.phone = payload.phone
        self.db.commit()
        refreshed = self.repo.get_by_id(user.id)
        assert refreshed is not None
        return serialize_user(refreshed)

    def create_address(self, user: User, payload: AddressCreate) -> Address:
        if payload.is_default:
            for existing in self.repo.list_addresses(user.id):
                existing.is_default = False
        address = Address(user_id=user.id, **payload.model_dump())
        self.db.add(address)
        self.db.commit()
        self.db.refresh(address)
        return address

    def update_address(
        self, user: User, address_id: uuid.UUID, payload: AddressUpdate
    ) -> Address:
        address = self.repo.get_address(address_id, user.id)
        if address is None:
            raise NotFoundError("Address not found.")
        data = payload.model_dump(exclude_unset=True)
        if data.get("is_default"):
            for existing in self.repo.list_addresses(user.id):
                existing.is_default = False
        for key, value in data.items():
            setattr(address, key, value)
        self.db.commit()
        self.db.refresh(address)
        return address

    def delete_address(self, user: User, address_id: uuid.UUID) -> None:
        address = self.repo.get_address(address_id, user.id)
        if address is None:
            raise NotFoundError("Address not found.")
        self.db.delete(address)
        self.db.commit()

    def create_user_as_super_admin(
        self, actor: User, payload: AdminUserCreateRequest
    ) -> UserResponse:
        email = payload.email.lower().strip()
        if self.repo.get_by_email(email) is not None:
            raise ConflictError("An account with this email already exists.")
        roles = self.repo.ensure_default_roles()
        role = roles[payload.role_name]
        user = User(
            role_id=role.id,
            email=email,
            full_name=payload.full_name.strip(),
            phone=payload.phone,
            password_hash=hash_password(payload.password),
            is_active=True,
        )
        self.db.add(user)
        self.db.flush()
        self.db.add(Cart(user_id=user.id))
        self.db.add(Wishlist(user_id=user.id))
        record_audit_log(
            self.db,
            actor_id=actor.id,
            action="SUPER_ADMIN_CREATED_USER",
            resource_type="user",
            resource_id=str(user.id),
            details={"role": payload.role_name, "email": email},
        )
        self.db.commit()
        created = self.repo.get_by_id(user.id)
        assert created is not None
        return serialize_user(created)

