from contextlib import asynccontextmanager
import logging
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import GlowCartError
from app.db.seed import ensure_initial_data
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings()
    # Log active CORS config so Railway deployment logs make it easy to debug
    logger.info(
        "CORS config: allow_origins=%s, allow_origin_regex=%s",
        settings.cors_origins,
        settings.cors_origin_regex,
    )
    if settings.auto_seed_on_startup:
        try:
            with SessionLocal() as db:
                seeded = ensure_initial_data(db)
                if seeded:
                    logger.info("GlowCart startup auto-seed applied missing catalog/admin records.")
        except Exception as exc:  # pragma: no cover - surfaced in startup logs if DB unreachable
            logger.exception("Startup auto-seed skipped or failed: %s", exc)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_origin_regex=settings.cors_origin_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    @app.exception_handler(GlowCartError)
    async def glowcart_error_handler(_request: Request, exc: GlowCartError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "code": exc.code},
        )

    @app.get("/health", tags=["Health"])
    def health_check():
        return {"status": "ok", "service": "glowcart-backend", "version": "1.0.0"}

    @app.get("/health/cors", tags=["Health"])
    def cors_debug():
        """Read-only CORS configuration dump for deployment debugging."""
        import os
        return {
            "cors_origins": settings.cors_origins,
            "cors_origin_regex": settings.cors_origin_regex,
            "app_env": settings.app_env,
            "railway_env_vars_detected": {
                k: bool(os.getenv(k))
                for k in (
                    "RAILWAY_ENVIRONMENT",
                    "RAILWAY_PROJECT_ID",
                    "RAILWAY_SERVICE_NAME",
                    "RAILWAY_PUBLIC_DOMAIN",
                    "RAILWAY_STATIC_URL",
                    "RAILWAY_GIT_REPO_NAME",
                    "RAILWAY_DEPLOYMENT_ID",
                    "CORS_ORIGINS",
                    "CORS_FRONTEND_URL",
                    "FRONTEND_URL",
                )
            },
        }

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    upload_path = Path(settings.local_upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(upload_path)), name="uploads")

    return app


app = create_app()
