# Deployment Guide — GlowCart

## 1. Architecture Summary
- **Frontend:** Vercel (`frontend/`), configured with `frontend/vercel.json` for SPA client-side routing.
- **Backend & PostgreSQL:** Railway (`backend/Dockerfile`) + Railway managed PostgreSQL.
- **Media Storage:** Cloudinary (optional; falls back to local `/uploads/products` if unset).

## 2. Railway Backend & PostgreSQL Setup
1. Create a Railway project and add a **PostgreSQL** service.
2. Deploy the `backend/` directory using `backend/Dockerfile`.
3. Configure Railway environment variables (never commit secrets):
   - `APP_ENV=production`
   - `DATABASE_URL=${{Postgres.DATABASE_URL}}` (use `postgresql+psycopg://` driver prefix)
   - `JWT_SECRET_KEY=<64-char-random-secret>`
   - `PAYMENT_WEBHOOK_SECRET=<random-hmac-secret>`
   - `CORS_ORIGINS=https://your-glowcart-app.vercel.app`
   - Optional Cloudinary: `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`
4. The Dockerfile startup command runs `alembic upgrade head` automatically before launching `uvicorn` on `$PORT`.
5. Verify health check at `GET https://<railway-domain>/health` -> `{"status": "ok"}`.

## 3. Vercel Frontend Setup
1. Import the repository into Vercel with Root Directory set to `frontend`.
2. Set Build Command: `npm run build`, Output Directory: `dist`.
3. Set Environment Variable: `VITE_API_BASE_URL=https://<railway-domain>/api/v1`.
4. `frontend/vercel.json` rewrites all routes to `/index.html` for React Router.

## 4. Security, Logging & Rollback Considerations
- Enforce HTTPS on both Vercel and Railway public domains.
- Never deploy with default `.env.example` secrets.
- Database backups: enable automated Railway PostgreSQL snapshots prior to schema migrations.
- Rollback: revert Railway deployment to previous image tag and execute `alembic downgrade -1` only if a migration was explicitly designed to be reversible.

