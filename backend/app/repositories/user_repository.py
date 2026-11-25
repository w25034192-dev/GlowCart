import uuid
from sqlalchemy.orm import Session, joinedload

from app.models import Address, Role, User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return (
            self.db.query(User)
            .options(joinedload(User.role))
            .filter(User.id == user_id)
            .first()
        )

    def get_by_email(self, email: str) -> User | None:
        return (
            self.db.query(User)
            .options(joinedload(User.role))
            .filter(User.email == email.lower().strip())
            .first()
        )

    def get_role_by_name(self, name: str) -> Role | None:
        return self.db.query(Role).filter(Role.name == name).first()

    def ensure_default_roles(self) -> dict[str, Role]:
        specs = {
            "customer": ("Standard shopper", ["catalog:read", "cart:write", "orders:own"]),
            "admin": (
                "Store administrator",
                ["catalog:write", "inventory:write", "orders:manage", "analytics:read"],
            ),
            "super_admin": ("Platform owner", ["*"]),
        }
        roles: dict[str, Role] = {}
        for name, (desc, perms) in specs.items():
            role = self.get_role_by_name(name)
            if role is None:
                role = Role(name=name, description=desc, permissions=perms)
                self.db.add(role)
                self.db.flush()
            roles[name] = role
        return roles

    def list_addresses(self, user_id: uuid.UUID) -> list[Address]:
        return (
            self.db.query(Address)
            .filter(Address.user_id == user_id)
            .order_by(Address.is_default.desc(), Address.created_at.desc())
            .all()
        )

    def get_address(self, address_id: uuid.UUID, user_id: uuid.UUID) -> Address | None:
        return (
            self.db.query(Address)
            .filter(Address.id == address_id, Address.user_id == user_id)
            .first()
        )

