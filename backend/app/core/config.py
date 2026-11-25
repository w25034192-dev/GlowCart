from functools import lru_cache
import os
from pathlib import Path
from pydantic import BaseModel, model_validator


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


class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "GlowCart API")
    app_env: str = os.getenv("APP_ENV", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    api_v1_prefix: str = os.getenv("API_V1_PREFIX", "/api/v1")

    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./glowcart_dev.db",
    )

    jwt_secret_key: str = os.getenv(
        "JWT_SECRET_KEY",
        "glowcart-dev-only-secret-key-change-in-production-min-32-chars",
    )
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    password_reset_token_expire_minutes: int = int(
        os.getenv("PASSWORD_RESET_TOKEN_EXPIRE_MINUTES", "30")
    )

    cors_origins: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
        ).split(",")
        if origin.strip()
    ]

    payment_webhook_secret: str = os.getenv(
        "PAYMENT_WEBHOOK_SECRET",
        "glowcart-sandbox-webhook-secret-change-me",
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

    @model_validator(mode="after")
    def _validate_production_secrets(self) -> "Settings":
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

