from datetime import datetime
import uuid
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=150)
    password: str = Field(min_length=8, max_length=128)
    phone: str | None = Field(default=None, max_length=40)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str | None = None


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class ProfileUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=150)
    phone: str | None = Field(default=None, max_length=40)


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    phone: str | None
    role: str
    is_active: bool
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class AddressCreate(BaseModel):
    label: str = Field(default="Home", max_length=60)
    recipient_name: str = Field(min_length=2, max_length=150)
    phone: str = Field(min_length=5, max_length=40)
    line1: str = Field(min_length=3, max_length=255)
    line2: str | None = Field(default=None, max_length=255)
    city: str = Field(min_length=2, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    postal_code: str = Field(min_length=2, max_length=30)
    country: str = Field(min_length=2, max_length=100)
    is_default: bool = False


class AddressUpdate(BaseModel):
    label: str | None = Field(default=None, max_length=60)
    recipient_name: str | None = Field(default=None, min_length=2, max_length=150)
    phone: str | None = Field(default=None, min_length=5, max_length=40)
    line1: str | None = Field(default=None, min_length=3, max_length=255)
    line2: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, min_length=2, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    postal_code: str | None = Field(default=None, min_length=2, max_length=30)
    country: str | None = Field(default=None, min_length=2, max_length=100)
    is_default: bool | None = None


class AddressResponse(BaseModel):
    id: uuid.UUID
    label: str
    recipient_name: str
    phone: str
    line1: str
    line2: str | None
    city: str
    state: str | None
    postal_code: str
    country: str
    is_default: bool


class AdminUserCreateRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=150)
    password: str = Field(min_length=8, max_length=128)
    role_name: str = Field(default="admin", pattern="^(customer|admin|super_admin)$")
    phone: str | None = Field(default=None, max_length=40)


class RoleAssignRequest(BaseModel):
    role_name: str = Field(pattern="^(customer|admin|super_admin)$")
    is_active: bool | None = None


class RolePermissionsUpdateRequest(BaseModel):
    permissions: list[str]
    description: str | None = None

