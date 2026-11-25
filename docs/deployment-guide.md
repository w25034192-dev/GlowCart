# Deployment Guide — GlowCart

## 1. Architecture Summary
- **Railway Full-Stack Docker Deployment (Recommended when deploying everything on Railway):**
  - **PostgreSQL Service:** Railway managed PostgreSQL.
  - **Backend Service (`backend/`):** Built from [`backend/Dockerfile`](../backend/Dockerfile) (`production` non-root stage) + [`backend/railway.toml`](../backend/railway.toml) + [`backend/start.sh`](../backend/start.sh).
  - **Frontend Service (`frontend/`):** Built from [`frontend/Dockerfile`](../frontend/Dockerfile) (`production` non-root Nginx stage) + [`frontend/railway.toml`](../frontend/railway.toml) + [`frontend/nginx.conf.template`](../frontend/nginx.conf.template).
- **Optional Split Deployment:** Frontend on **Vercel** (`frontend/vercel.json`) + Backend & PostgreSQL on **Railway**.
- **Media Storage:** Cloudinary (optional; falls back to `/app/uploads/products` if unset).

---

## 2. Railway Setup (Backend + Frontend + PostgreSQL)

### A. PostgreSQL Service
1. Create a Railway project and add a **PostgreSQL** service.
2. Railway exposes `${{Postgres.DATABASE_URL}}` (e.g., `postgresql://...`). GlowCart automatically normalizes `postgres://` and `postgresql://` to `postgresql+psycopg://` in `backend/app/core/config.py`.

### B. Backend Service (`backend/`)
1. Create a Railway service pointing to this repository with **Root Directory** set to `backend`.
2. Railway automatically reads `backend/railway.toml` (`builder = "DOCKERFILE"`, `healthcheckPath = "/health"`).
3. Configure Railway environment variables (never commit real secrets):
   - `APP_ENV=production`
   - `DATABASE_URL=${{Postgres.DATABASE_URL}}`
   - `JWT_SECRET_KEY=<64-char-random-secret>`
   - `PAYMENT_WEBHOOK_SECRET=<random-hmac-secret>`
   - `CORS_ORIGINS=https://<your-frontend-service>.up.railway.app` (or Vercel URL)
   - `SEED_DEMO_DATA=true` *(optional first deploy only; set `false` afterwards)*
   - Optional Cloudinary: `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`
4. `backend/start.sh` automatically runs `alembic upgrade head` before starting `uvicorn` on `$PORT` with `--proxy-headers`.
5. Verify health check: `GET https://<backend-domain>/health` → `{"status": "ok"}`.

### C. Frontend Service (`frontend/`)
1. Create a second Railway service in the same project with **Root Directory** set to `frontend`.
2. Railway automatically reads `frontend/railway.toml` (`builder = "DOCKERFILE"`, `healthcheckPath = "/healthz"`).
3. Configure Railway build/runtime variable:
   - `VITE_API_BASE_URL=https://<backend-domain>/api/v1` *(Vite reads this at Docker build time via `ARG VITE_API_BASE_URL`)*.
4. Nginx serves the React SPA (`try_files $uri $uri/ /index.html;`) on Railway's dynamic `$PORT`.
5. Verify health check: `GET https://<frontend-domain>/healthz` → `ok`.

---

## 3. Local Docker Compose Development
- **Hot-reload development stack (`db` + `backend` + `frontend`):**
  ```bash
  docker compose up --build
  ```
  - Frontend: `http://localhost:5173`
  - Backend API & Swagger: `http://localhost:8000/docs`
- **Production-image local simulation (non-root containers + Nginx):**
  ```bash
  docker compose -f docker-compose.prod.yml up --build
  ```
  - Frontend (Nginx): `http://localhost:8080`
  - Backend API: `http://localhost:8000`

---

## 4. Vercel Alternative for Frontend
1. Import the repository into Vercel with Root Directory set to `frontend`.
2. Build Command: `npm run build`, Output Directory: `dist`.
3. Set `VITE_API_BASE_URL=https://<railway-backend-domain>/api/v1`.

---

## 5. Security, Backups & Rollback
- Enforce HTTPS on all Railway/Vercel public domains.
- Never deploy with `.env.example` secrets (`APP_ENV=production` fails closed on default secrets).
- Enable automated Railway PostgreSQL backups before schema migrations.
- Rollback: redeploy the previous Railway image and run `alembic downgrade -1` only for explicitly reversible migrations.
