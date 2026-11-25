import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import require_roles
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models import AuditLog, Role, User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    AdminUserCreateRequest,
    RoleAssignRequest,
    RolePermissionsUpdateRequest,
    UserResponse,
)
from app.services.audit_service import record_audit_log
from app.services.auth_service import AuthService, serialize_user

router = APIRouter(prefix="/admin", tags=["Admin & Super Admin"])

# In-memory/runtime store for non-secret store configuration settings
_SYSTEM_SETTINGS: dict = {
    "store_name": "GlowCart",
    "base_currency": "USD",
    "default_shipping_fee": 5.00,
    "free_shipping_threshold": 75.00,
    "near_expiry_days": 60,
    "allow_customer_cancellations": True,
}


@router.get("/customers", response_model=list[UserResponse])
def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    _admin: User = Depends(require_roles("admin", "super_admin")),
    db: Session = Depends(get_db),
):
    users = (
        db.query(User)
        .options(joinedload(User.role))
        .order_by(User.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [serialize_user(u) for u in users]


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_admin_or_user(
    payload: AdminUserCreateRequest,
    actor: User = Depends(require_roles("super_admin")),
    db: Session = Depends(get_db),
):
    return AuthService(db).create_user_as_super_admin(actor, payload)


@router.patch("/users/{user_id}/role", response_model=UserResponse)
def assign_user_role(
    user_id: uuid.UUID,
    payload: RoleAssignRequest,
    actor: User = Depends(require_roles("super_admin")),
    db: Session = Depends(get_db),
):
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if user is None:
        raise NotFoundError("User not found.")
    roles = repo.ensure_default_roles()
    user.role_id = roles[payload.role_name].id
    if payload.is_active is not None:
        user.is_active = payload.is_active
    record_audit_log(
        db,
        actor_id=actor.id,
        action="ROLE_UPDATED",
        resource_type="user",
        resource_id=str(user.id),
        details={"role": payload.role_name, "is_active": user.is_active},
    )
    db.commit()
    updated = repo.get_by_id(user.id)
    assert updated is not None
    return serialize_user(updated)


@router.get("/roles")
def list_roles(
    _actor: User = Depends(require_roles("super_admin")),
    db: Session = Depends(get_db),
):
    UserRepository(db).ensure_default_roles()
    db.commit()
    roles = db.query(Role).order_by(Role.name).all()
    return [
        {
            "id": str(r.id),
            "name": r.name,
            "description": r.description,
            "permissions": r.permissions,
        }
        for r in roles
    ]


@router.put("/roles/{role_name}")
def update_role_permissions(
    role_name: str,
    payload: RolePermissionsUpdateRequest,
    actor: User = Depends(require_roles("super_admin")),
    db: Session = Depends(get_db),
):
    role = db.query(Role).filter(Role.name == role_name).first()
    if role is None:
        raise NotFoundError("Role not found.")
    role.permissions = payload.permissions
    if payload.description is not None:
        role.description = payload.description
    record_audit_log(
        db,
        actor_id=actor.id,
        action="ROLE_PERMISSIONS_UPDATED",
        resource_type="role",
        resource_id=str(role.id),
        details={"role": role_name, "permissions": payload.permissions},
    )
    db.commit()
    return {"id": str(role.id), "name": role.name, "permissions": role.permissions}


@router.get("/audit-logs")
def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    _actor: User = Depends(require_roles("super_admin")),
    db: Session = Depends(get_db),
):
    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [
        {
            "id": str(log.id),
            "actor_id": str(log.actor_id) if log.actor_id else None,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "details": log.details,
            "ip_address": log.ip_address,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]


@router.get("/settings")
def get_system_settings(_actor: User = Depends(require_roles("admin", "super_admin"))):
    return _SYSTEM_SETTINGS


@router.put("/settings")
def update_system_settings(
    payload: dict,
    actor: User = Depends(require_roles("super_admin")),
    db: Session = Depends(get_db),
):
    allowed_keys = set(_SYSTEM_SETTINGS.keys())
    for key, value in payload.items():
        if key in allowed_keys:
            _SYSTEM_SETTINGS[key] = value
    record_audit_log(
        db,
        actor_id=actor.id,
        action="SYSTEM_SETTINGS_UPDATED",
        resource_type="settings",
        details={k: v for k, v in payload.items() if k in allowed_keys},
    )
    db.commit()
    return _SYSTEM_SETTINGS

