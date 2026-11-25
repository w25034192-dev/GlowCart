from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_token_payload, get_current_user
from app.core.config import get_settings
from app.core.rate_limiter import enforce_rate_limit
from app.db.session import get_db
from app.models import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    ProfileUpdateRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import AuthService, serialize_user

router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_settings()
auth_rate_limit = enforce_rate_limit("auth", settings.rate_limit_auth_per_minute)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(auth_rate_limit)],
)
def register(payload: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    ip = request.client.host if request.client else None
    return AuthService(db).register(payload, ip_address=ip)


@router.post(
    "/login",
    response_model=TokenResponse,
    dependencies=[Depends(auth_rate_limit)],
)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    ip = request.client.host if request.client else None
    return AuthService(db).login(payload, ip_address=ip)


@router.post("/refresh", response_model=TokenResponse)
def refresh_tokens(payload: RefreshRequest, db: Session = Depends(get_db)):
    return AuthService(db).refresh(payload.refresh_token)


@router.post("/logout")
def logout(
    body: LogoutRequest | None = None,
    token_payload: dict = Depends(get_current_token_payload),
    db: Session = Depends(get_db),
):
    AuthService(db).logout(
        access_jti=token_payload.get("jti"),
        refresh_token=body.refresh_token if body else None,
    )
    return {"message": "Logged out successfully."}


@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)):
    return serialize_user(user)


@router.put("/me", response_model=UserResponse)
def update_me(
    payload: ProfileUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AuthService(db).update_profile(user, payload)


@router.post("/forgot-password", dependencies=[Depends(auth_rate_limit)])
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    return AuthService(db).forgot_password(payload.email)


@router.post("/reset-password", dependencies=[Depends(auth_rate_limit)])
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    AuthService(db).reset_password(payload.token, payload.new_password)
    return {"message": "Password has been reset successfully."}

