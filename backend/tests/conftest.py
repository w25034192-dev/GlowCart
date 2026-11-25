import os
from pathlib import Path
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_glowcart.db")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-at-least-32-chars-long")
os.environ.setdefault("PAYMENT_WEBHOOK_SECRET", "test-webhook-secret-key")
os.environ.setdefault("AUTO_SEED_ON_STARTUP", "false")

from app.core.rate_limiter import rate_limiter
from app.core.security import hash_password, reset_revoked_tokens
from app.db.session import get_db
from app.main import create_app
from app.models import Base, Cart, Role, User, Wishlist


@pytest.fixture()
def db_engine(tmp_path):
    db_file = tmp_path / "test_glowcart.db"
    engine = create_engine(
        f"sqlite:///{db_file}",
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(engine, "connect")
    def _enable_fk(dbapi_connection, _record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture()
def session_factory(db_engine):
    TestingSessionLocal = sessionmaker(
        bind=db_engine, autoflush=False, autocommit=False, expire_on_commit=False
    )
    with TestingSessionLocal() as s:
        seed_base_roles(s)
    return TestingSessionLocal


@pytest.fixture()
def db_session(session_factory):
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


def seed_base_roles(session: Session) -> dict[str, Role]:
    roles_spec = [
        ("customer", "Standard shopper", ["catalog:read", "cart:write", "orders:own"]),
        ("admin", "Store administrator", ["catalog:write", "inventory:write", "orders:manage", "analytics:read"]),
        ("super_admin", "Platform owner", ["*"]),
    ]
    roles: dict[str, Role] = {}
    for name, desc, perms in roles_spec:
        existing = session.query(Role).filter(Role.name == name).first()
        if existing is None:
            existing = Role(name=name, description=desc, permissions=perms)
            session.add(existing)
            session.flush()
        roles[name] = existing
    session.commit()
    return roles


@pytest.fixture()
def client(session_factory):
    rate_limiter.reset()
    reset_revoked_tokens()
    app = create_app()

    def _override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def make_user(db_session: Session):
    def _make_user(
        email: str,
        password: str = "GlowCartPass123!",
        role_name: str = "customer",
        full_name: str = "Test User",
    ) -> User:
        role = db_session.query(Role).filter(Role.name == role_name).one()
        user = User(
            role_id=role.id,
            email=email,
            full_name=full_name,
            password_hash=hash_password(password),
            is_active=True,
        )
        db_session.add(user)
        db_session.flush()
        db_session.add(Cart(user_id=user.id))
        db_session.add(Wishlist(user_id=user.id))
        db_session.commit()
        db_session.refresh(user)
        return user

    return _make_user
