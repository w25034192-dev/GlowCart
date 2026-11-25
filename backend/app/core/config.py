from functools import lru_cache
import os
from pathlib import Path
from pydantic import BaseModel, Field, model_validator


def _load_dotenv() -> None:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.is_file():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv()

_DEFAULT_CORS_ORIGINS = ("http://localhost:5173", "http://127.0.0.1:5173")
_RAILWAY_CORS_ORIGIN_REGEX = (
    r"^https://[a-zA-Z0-9-]+(\.up\.railway\.app|\.vercel\.app|\.netlify\.app)$"
)


def _normalize_origin(origin: str) -> str:
    return origin.strip().strip('"').strip("'").rstrip("/")


def _default_cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", ",".join(_DEFAULT_CORS_ORIGINS))
    origins = [_normalize_origin(o) for o in raw.split(",") if _normalize_origin(o)]
    for extra_key in ("FRONTEND_URL", "PUBLIC_FRONTEND_URL"):
        extra = _normalize_origin(os.getenv(extra_key, ""))
        if extra and extra not in origins:
            origins.append(extra)
    # On Railway, RAILWAY_PUBLIC_DOMAIN is the backend's own public domain.
    # Also auto-add any explicit CORS_FRONTEND_URL the user sets in Railway vars.
    for extra_key in ("RAILWAY_PUBLIC_DOMAIN", "CORS_FRONTEND_URL"):
        raw_domain = os.getenv(extra_key, "").strip()
        if not raw_domain:
            continue
        # RAILWAY_PUBLIC_DOMAIN is just the hostname (no scheme)
        if not raw_domain.startswith("http"):
            raw_domain = f"https://{raw_domain}"
        extra = _normalize_origin(raw_domain)
        if extra and extra not in origins:
            origins.append(extra)
    return origins


def _default_cors_origin_regex() -> str | None:
    explicit = os.getenv("CORS_ORIGIN_REGEX", "").strip()
    if explicit:
        return explicit
    # Detect Railway via any of the many env vars it injects
    is_railway = bool(
        os.getenv("RAILWAY_ENVIRONMENT")
        or os.getenv("RAILWAY_PROJECT_ID")
        or os.getenv("RAILWAY_SERVICE_NAME")
        or os.getenv("RAILWAY_PUBLIC_DOMAIN")
        or os.getenv("RAILWAY_STATIC_URL")
        or os.getenv("RAILWAY_GIT_REPO_NAME")
        or os.getenv("RAILWAY_DEPLOYMENT_ID")
    )
    # Also treat APP_ENV=production as a signal to allow Railway/Vercel origins
    # unless the user has explicitly listed CORS_ORIGINS (meaning they want tight control)
    is_production = os.getenv("APP_ENV", "").lower() == "production"
    if (is_railway or is_production) and not os.getenv("CORS_ORIGINS", "").strip():
        return _RAILWAY_CORS_ORIGIN_REGEX
    return None


class Settings(BaseModel):
    app_name: str = Field(default_factory=lambda: os.getenv("APP_NAME", "GlowCart API"))
    app_env: str = Field(default_factory=lambda: os.getenv("APP_ENV", "development"))
    debug: bool = Field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")
    api_v1_prefix: str = Field(default_factory=lambda: os.getenv("API_V1_PREFIX", "/api/v1"))

    database_url: str = Field(
        default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./glowcart_dev.db")
    )

    jwt_secret_key: str = Field(
        default_factory=lambda: os.getenv(
            "JWT_SECRET_KEY",
            "glowcart-dev-only-secret-key-change-in-production-min-32-chars",
        )
    )
    jwt_algorithm: str = Field(default_factory=lambda: os.getenv("JWT_ALGORITHM", "HS256"))
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    password_reset_token_expire_minutes: int = int(
        os.getenv("PASSWORD_RESET_TOKEN_EXPIRE_MINUTES", "30")
    )

    cors_origins: list[str] = Field(default_factory=_default_cors_origins)
    cors_origin_regex: str | None = Field(default_factory=_default_cors_origin_regex)

    payment_webhook_secret: str = Field(
        default_factory=lambda: os.getenv(
            "PAYMENT_WEBHOOK_SECRET",
            "glowcart-sandbox-webhook-secret-change-me",
        )
    )

    cloudinary_cloud_name: str = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    cloudinary_api_key: str = os.getenv("CLOUDINARY_API_KEY", "")
    cloudinary_api_secret: str = os.getenv("CLOUDINARY_API_SECRET", "")
    local_upload_dir: str = os.getenv("LOCAL_UPLOAD_DIR", "uploads")

    rate_limit_auth_per_minute: int = int(os.getenv("RATE_LIMIT_AUTH_PER_MINUTE", "60"))
    rate_limit_payment_per_minute: int = int(
        os.getenv("RATE_LIMIT_PAYMENT_PER_MINUTE", "60")
    )

    default_shipping_fee: float = float(os.getenv("DEFAULT_SHIPPING_FEE", "5.00"))
    free_shipping_threshold: float = float(os.getenv("FREE_SHIPPING_THRESHOLD", "75.00"))
    auto_seed_on_startup: bool = os.getenv("AUTO_SEED_ON_STARTUP", "true").lower() == "true"

    @model_validator(mode="after")
    def _validate_and_normalize(self) -> "Settings":
        self.cors_origins = [
            _normalize_origin(o) for o in self.cors_origins if _normalize_origin(o)
        ]
        if self.database_url.startswith("postgres://"):
            self.database_url = "postgresql+psycopg://" + self.database_url[len("postgres://") :]
        elif self.database_url.startswith("postgresql://"):
            self.database_url = "postgresql+psycopg://" + self.database_url[len("postgresql://") :]

        if self.app_env.lower() == "production":
            dev_jwt = "glowcart-dev-only-secret-key-change-in-production-min-32-chars"
            dev_wh = "glowcart-sandbox-webhook-secret-change-me"
            if (
                not self.jwt_secret_key
                or self.jwt_secret_key == dev_jwt
                or len(self.jwt_secret_key) < 32
            ):
                raise ValueError("JWT_SECRET_KEY must be set to a strong 32+ char secret in production.")
            if not self.payment_webhook_secret or self.payment_webhook_secret == dev_wh:
                raise ValueError("PAYMENT_WEBHOOK_SECRET must be set to a non-default secret in production.")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()

