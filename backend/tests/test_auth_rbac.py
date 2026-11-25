def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_register_login_refresh_me_and_logout(client):
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": "clara@glowcart.com",
            "full_name": "Clara Beauty",
            "password": "StrongPassword123!",
        },
    )
    assert reg.status_code == 201
    assert reg.json()["email"] == "clara@glowcart.com"
    assert reg.json()["role"] == "customer"

    dup = client.post(
        "/api/v1/auth/register",
        json={
            "email": "clara@glowcart.com",
            "full_name": "Clara Duplicate",
            "password": "StrongPassword123!",
        },
    )
    assert dup.status_code == 409

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "clara@glowcart.com", "password": "StrongPassword123!"},
    )
    assert login.status_code == 200
    tokens = login.json()
    assert tokens["access_token"]
    assert tokens["refresh_token"]

    me = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json()["email"] == "clara@glowcart.com"

    refreshed = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refreshed.status_code == 200
    assert refreshed.json()["access_token"]

    logout = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": tokens["refresh_token"]},
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert logout.status_code == 200

    reused = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert reused.status_code == 401


def test_forgot_and_reset_password(client, make_user):
    make_user("resetme@glowcart.com", password="OldPassword123!")
    forgot = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "resetme@glowcart.com"},
    )
    assert forgot.status_code == 200
    reset_token = forgot.json()["reset_token"]

    reset = client.post(
        "/api/v1/auth/reset-password",
        json={"token": reset_token, "new_password": "NewPassword456!"},
    )
    assert reset.status_code == 200

    old_login = client.post(
        "/api/v1/auth/login",
        json={"email": "resetme@glowcart.com", "password": "OldPassword123!"},
    )
    assert old_login.status_code == 401

    new_login = client.post(
        "/api/v1/auth/login",
        json={"email": "resetme@glowcart.com", "password": "NewPassword456!"},
    )
    assert new_login.status_code == 200


def test_customer_cannot_access_admin_or_super_admin_endpoints(client, make_user):
    make_user("shopper@glowcart.com", role_name="customer")
    make_user("admin@glowcart.com", role_name="admin")
    make_user("owner@glowcart.com", role_name="super_admin")

    cust_token = client.post(
        "/api/v1/auth/login",
        json={"email": "shopper@glowcart.com", "password": "GlowCartPass123!"},
    ).json()["access_token"]
    admin_token = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@glowcart.com", "password": "GlowCartPass123!"},
    ).json()["access_token"]
    super_token = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@glowcart.com", "password": "GlowCartPass123!"},
    ).json()["access_token"]

    res_cust = client.get(
        "/api/v1/admin/audit-logs",
        headers={"Authorization": f"Bearer {cust_token}"},
    )
    assert res_cust.status_code == 403

    res_admin = client.get(
        "/api/v1/admin/audit-logs",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_admin.status_code == 403

    res_super = client.get(
        "/api/v1/admin/audit-logs",
        headers={"Authorization": f"Bearer {super_token}"},
    )
    assert res_super.status_code == 200


def test_profile_and_address_crud(client, make_user):
    make_user("addr@glowcart.com", role_name="customer")
    token = client.post(
        "/api/v1/auth/login",
        json={"email": "addr@glowcart.com", "password": "GlowCartPass123!"},
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    prof = client.put(
        "/api/v1/auth/me",
        json={"full_name": "Updated Name", "phone": "+1-555-0101"},
        headers=headers,
    )
    assert prof.status_code == 200
    assert prof.json()["full_name"] == "Updated Name"

    addr = client.post(
        "/api/v1/addresses",
        json={
            "label": "Home",
            "recipient_name": "Updated Name",
            "phone": "+1-555-0101",
            "line1": "123 Rose Ave",
            "city": "New York",
            "state": "NY",
            "postal_code": "10001",
            "country": "United States",
            "is_default": True,
        },
        headers=headers,
    )
    assert addr.status_code == 201
    addr_id = addr.json()["id"]

    listed = client.get("/api/v1/addresses", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    deleted = client.delete(f"/api/v1/addresses/{addr_id}", headers=headers)
    assert deleted.status_code == 204


def test_production_settings_reject_default_secrets():
    import pytest
    from app.core.config import Settings

    with pytest.raises(ValueError):
        Settings(
            app_env="production",
            jwt_secret_key="glowcart-dev-only-secret-key-change-in-production-min-32-chars",
        )
    with pytest.raises(ValueError):
        Settings(
            app_env="production",
            jwt_secret_key="a" * 32,
            payment_webhook_secret="glowcart-sandbox-webhook-secret-change-me",
        )


def test_railway_postgres_url_normalization():
    from app.core.config import Settings

    s1 = Settings(database_url="postgres://user:pass@pg.railway.internal:5432/railway")
    assert s1.database_url == "postgresql+psycopg://user:pass@pg.railway.internal:5432/railway"

    s2 = Settings(database_url="postgresql://user:pass@pg.railway.internal:5432/railway")
    assert s2.database_url == "postgresql+psycopg://user:pass@pg.railway.internal:5432/railway"

    s3 = Settings(database_url="sqlite:///./glowcart_dev.db")
    assert s3.database_url == "sqlite:///./glowcart_dev.db"


def test_cors_origins_normalization_and_railway_preflight(monkeypatch):
    from fastapi.testclient import TestClient
    from app.core.config import Settings, get_settings, _default_cors_origin_regex
    from app.main import create_app

    s = Settings(
        cors_origins=[
            ' "https://glowcart-frontend.up.railway.app/" ',
            "https://glowcart.vercel.app/",
        ]
    )
    assert s.cors_origins == [
        "https://glowcart-frontend.up.railway.app",
        "https://glowcart.vercel.app",
    ]

    # --- Regex coverage: all production subdomain forms must match ---
    import re
    from app.core.config import _DEFAULT_CORS_ORIGIN_REGEX
    should_match = [
        "https://glowcart-production-7b775f24.up.railway.app",
        "https://glowcart-frontend.up.railway.app",
        "https://glowcart.vercel.app",
        "https://my-app.netlify.app",
        "http://localhost:5173",
    ]
    should_not_match = [
        "https://evil.com",
        "https://glowcart-frontend.up.railway.app.evil.com",
    ]
    for origin in should_match:
        assert re.fullmatch(_DEFAULT_CORS_ORIGIN_REGEX, origin), f"Should match: {origin}"
    for origin in should_not_match:
        assert not re.fullmatch(_DEFAULT_CORS_ORIGIN_REGEX, origin), f"Should NOT match: {origin}"

    # --- RAILWAY_PUBLIC_DOMAIN auto-inject into cors_origins ---
    monkeypatch.setenv("RAILWAY_PUBLIC_DOMAIN", "glowcart-production-7b775f24.up.railway.app")
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    monkeypatch.delenv("FRONTEND_URL", raising=False)
    monkeypatch.delenv("PUBLIC_FRONTEND_URL", raising=False)
    monkeypatch.delenv("CORS_FRONTEND_URL", raising=False)
    get_settings.cache_clear()
    s2 = Settings()
    assert "https://glowcart-production-7b775f24.up.railway.app" in s2.cors_origins
    monkeypatch.delenv("RAILWAY_PUBLIC_DOMAIN", raising=False)

    # --- CORS_FRONTEND_URL env var ---
    monkeypatch.setenv("CORS_FRONTEND_URL", "https://my-custom-frontend.up.railway.app")
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    get_settings.cache_clear()
    s3 = Settings()
    assert "https://my-custom-frontend.up.railway.app" in s3.cors_origins
    monkeypatch.delenv("CORS_FRONTEND_URL", raising=False)

    # --- is_production fallback: APP_ENV=production enables regex even without Railway vars ---
    monkeypatch.delenv("RAILWAY_ENVIRONMENT", raising=False)
    monkeypatch.delenv("RAILWAY_PROJECT_ID", raising=False)
    monkeypatch.delenv("RAILWAY_SERVICE_NAME", raising=False)
    monkeypatch.delenv("RAILWAY_PUBLIC_DOMAIN", raising=False)
    monkeypatch.delenv("RAILWAY_STATIC_URL", raising=False)
    monkeypatch.delenv("RAILWAY_GIT_REPO_NAME", raising=False)
    monkeypatch.delenv("RAILWAY_DEPLOYMENT_ID", raising=False)
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    monkeypatch.setenv("APP_ENV", "production")
    regex = _default_cors_origin_regex()
    assert regex is not None, "APP_ENV=production should activate CORS regex"
    assert re.match(regex, "https://glowcart-production-7b775f24.up.railway.app")

    # When running on Railway, HTTPS *.up.railway.app origins work via regex
    get_settings.cache_clear()
    monkeypatch.setenv("RAILWAY_ENVIRONMENT", "production")
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("JWT_SECRET_KEY", "x" * 64)
    monkeypatch.setenv("PAYMENT_WEBHOOK_SECRET", "y" * 32)
    try:
        app = create_app()
        with TestClient(app) as tc:
            origin = "https://glowcart-production-7b775f24.up.railway.app"
            preflight = tc.options(
                "/api/v1/products",
                headers={
                    "Origin": origin,
                    "Access-Control-Request-Method": "GET",
                    "Access-Control-Request-Headers": "Authorization,Content-Type",
                },
            )
            assert preflight.status_code == 200
            assert preflight.headers.get("access-control-allow-origin") == origin
            assert preflight.headers.get("access-control-allow-credentials") == "true"

            # Also verify the /health/cors debug endpoint works
            cors_debug = tc.get("/health/cors")
            assert cors_debug.status_code == 200
            data = cors_debug.json()
            assert "cors_origin_regex" in data
            assert data["cors_origin_regex"] is not None
    finally:
        get_settings.cache_clear()


