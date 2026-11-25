# Latest Session Context — GlowCart

> **Updated:** 2026-11-25 (Session 3 — Final Production CORS & Railway Database URL Configuration)  
> **Current Focus:** Rock-solid production CORS defaults + Railway internal PostgreSQL connection guide + commit push

## What Was Diagnosed & Fixed

1. **CORS Missing Header & Preflight 400 Root Cause:**
   - Previous curl testing to the deployed backend confirmed:
     - `OPTIONS` returned `HTTP 400 Disallowed CORS origin` when called from frontend domain.
     - `GET /api/v1/products` returned HTTP 200 but **omitted `Access-Control-Allow-Origin`** for cross-origin requests.
     - Browsers strictly enforce CORS: any cross-origin HTTP 200 without `Access-Control-Allow-Origin` causes Axios to throw `AxiosError: Network Error`.
   - **Fix:** In [`backend/app/core/config.py`](../backend/app/core/config.py), set `_DEFAULT_CORS_ORIGIN_REGEX` to:
     `^https?://([a-zA-Z0-9-]+\.)*(up\.railway\.app|vercel\.app|netlify\.app|localhost|127\.0\.0\.1)(:\d+)?$`
     and ensured that unless an explicit custom list is passed in `CORS_ORIGINS`, this regex is **always active** across all deployment stages without relying on brittle Railway environment variable detection.
   - Added `/health/cors` diagnostic endpoint on backend to inspect active CORS configuration in production at any time.

2. **Railway Internal Database URL Configuration:**
   - User requested database URL:
     `postgresql://postgres:NOIXPjXvvxArHjGTOCNwMubaNSFquLvN@postgres.railway.internal:5432/railway`
   - Updated [`backend/.env.example`](../backend/.env.example) and created local `backend/.env` with this URL.
   - Verified that `backend/app/core/config.py` automatically normalizes `postgresql://` -> `postgresql+psycopg://` for SQLAlchemy 2.0.
   - Note: `postgres.railway.internal:5432` is a private network address only resolvable inside Railway's private network; local tests safely use SQLite.

## Verified Checks
- `cd backend && python3 -m pytest tests -v`: **23 passed, 0 failed** (`20.19s`, exit code `0`).
- `cd frontend && npm run build`: **clean build** (`2.27s`, exit code `0`).
- `cd frontend && npm test -- --run`: **8 passed, 0 failed** (`1.66s`, exit code `0`).
- Docker build: `COPY --chmod=755` verified.

## Next Steps for User
1. Push committed changes to trigger Railway backend redeploy.
2. Ensure Railway Backend service has:
   - `DATABASE_URL`: `postgresql://postgres:NOIXPjXvvxArHjGTOCNwMubaNSFquLvN@postgres.railway.internal:5432/railway`
   - `AUTO_SEED_ON_STARTUP`: `true`
3. Ensure Railway Frontend service has:
   - `VITE_API_BASE_URL`: `https://glowcart-production-7b775f24.up.railway.app/api/v1`

