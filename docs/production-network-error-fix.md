# Production Frontend "Network Error" — Investigation, Root Causes & Fixes

> **Date:** 2026-11-25  
> **Scope:** Frontend Axios client & Docker/Nginx runtime configuration, FastAPI `CORSMiddleware`, Railway deployment env handling, and 50-product catalog pagination verification.

---

## 0. Docker Build Failure — `chmod` in `nginx-unprivileged` (Fix Applied 2026-11-25)

### Root Cause
`nginxinc/nginx-unprivileged:1.27-alpine` runs as UID 101 (`nginx`) throughout the entire Docker build — it **never** runs as root. The `/docker-entrypoint.d/` directory is owned by root, so a `RUN chmod +x` on a file inside it fails:

```
chmod: /docker-entrypoint.d/99-glowcart-env.sh: Operation not permitted
```

### Fix — `COPY --chmod=755` (BuildKit inline permission)
Replaced the two-instruction pattern:
```dockerfile
# BEFORE (broken)
COPY docker-entrypoint-env.sh /docker-entrypoint.d/99-glowcart-env.sh
RUN chmod +x /docker-entrypoint.d/99-glowcart-env.sh
```
With a single BuildKit `COPY --chmod` instruction:
```dockerfile
# AFTER (fixed)
COPY --chmod=755 docker-entrypoint-env.sh /docker-entrypoint.d/99-glowcart-env.sh
```

`COPY --chmod` sets the file mode **inside the layer** at copy time — no shell permission change required, works under UID 101, and requires no `USER root` escalation. The `# syntax=docker/dockerfile:1` directive was already present at the top of the Dockerfile, so BuildKit features (including `--chmod`) are enabled.

Railway uses BuildKit by default, so this fix works without any Railway configuration changes.

### Verified
- `frontend/Dockerfile` updated: single `COPY --chmod=755` on line 32
- `cd backend && python3 -m pytest tests -v` → **23 passed, 0 failed** (exit 0)
- `cd frontend && npm run build` → **clean** (exit 0)
- `cd frontend && npm test -- --run` → **8 passed, 0 failed** (exit 0)

---

## 1. Investigation Summary (Phases 1 & 2)

1. **Frontend API Configuration & URL Construction (`frontend/src/services/api.ts`, `utils/media.ts`, `pages/admin/AdminOperationsPages.tsx`):**
   - Previously read `import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'` inline at Vite build time.
   - `apiClient.get('/products', { params })` and `catalogApi.getCategories()` do **not** duplicate `/api/v1` in source code, and `PaginatedProducts` (`{ items, total, page, page_size, total_pages }`) matches `backend/app/schemas/catalog.py` exactly.
   - **Root Cause A (Build-Time Env Freeze / Missing Runtime Config):** `frontend/Dockerfile` passed `ARG VITE_API_BASE_URL=http://localhost:8000/api/v1` only at Docker build time (`RUN npm run build`). If Railway built the image without `VITE_API_BASE_URL` (or added/changed it later as a runtime variable), the compiled Nginx bundle (`dist/assets/index-*.js`) called `http://localhost:8000/api/v1`, failing in visitors' browsers with Axios `"Network Error"`.
   - **Root Cause B (Unnormalized `VITE_API_BASE_URL` Forms):** Providing a bare domain (`https://backend.up.railway.app` without `/api/v1`), trailing slash (`.../api/v1/` causing `//auth/refresh`), duplicate `/api/v1/api/v1`, missing scheme, or `http://` from an `https://` page caused 404/CORS or Mixed Content `"Network Error"`.
2. **FastAPI `CORSMiddleware` (`backend/app/core/config.py`, `backend/app/main.py`):**
   - **Root Cause C (CORS Default Lockout & Origin Normalization):** `CORS_ORIGINS` defaulted solely to `http://localhost:5173,http://127.0.0.1:5173`, and `Settings` read `os.getenv` at class-definition time without stripping trailing `/` or surrounding quotes. Any Railway deployment without an exact trailing-slash-free `CORS_ORIGINS` caused browsers to block `GET /api/v1/products` and `GET /api/v1/categories` with Axios `"Network Error"` even while backend Swagger UI and direct `curl` returned `200 OK`.

---

## 2. Files Changed & Fixes Implemented (Phase 3)

| File | Change |
|---|---|
| `frontend/src/utils/apiConfig.ts` | Added `resolveApiBaseUrl()`, `API_BASE_URL`, and `BACKEND_ORIGIN` with runtime `window.__GLOWCART_CONFIG__` priority, scheme normalization, HTTPS mixed-content upgrade for remote hosts, trailing-slash removal, and single `/api/v1` enforcement |
| `frontend/src/services/api.ts` | Replaced inline fallback with normalized `API_BASE_URL` |
| `frontend/src/utils/media.ts` | Reused `BACKEND_ORIGIN` for `/uploads/...` media URLs |
| `frontend/src/pages/admin/AdminOperationsPages.tsx` | Reused `API_BASE_URL` for CSV report export links |
| `frontend/src/pages/customer/CatalogPage.tsx` | Displayed resolved `API endpoint: ${API_BASE_URL}/products` inside the `role="alert"` error card for instant diagnostics |
| `frontend/public/env-config.js` & `frontend/index.html` | Loaded `/env-config.js` before `src/main.tsx` |
| `frontend/docker-entrypoint-env.sh`, `frontend/Dockerfile`, `frontend/nginx.conf.template` | Generated `/tmp/env-config.js` at non-root Nginx container startup from `VITE_API_BASE_URL` / `API_BASE_URL` / `BACKEND_PUBLIC_URL` (`Cache-Control: no-store`) so runtime env changes work without rebuilding |
| `backend/app/core/config.py` & `backend/app/main.py` | Switched `Settings` fields to `default_factory`, normalized `CORS_ORIGINS` (quotes/whitespace/trailing `/`), added `FRONTEND_URL` / `PUBLIC_FRONTEND_URL` support, and enabled `allow_origin_regex` (`^https://([a-zA-Z0-9-]+\\.)?(up\\.railway\\.app|vercel\\.app)$`) automatically on Railway when `CORS_ORIGINS` is unset |
| `backend/tests/test_auth_rbac.py`, `backend/tests/test_catalog_inventory.py`, `frontend/src/test/App.test.tsx` | Added CORS normalization & Railway `OPTIONS` preflight test, 50-product pagination (pages 1–5) test, URL normalizer tests, and frontend 5-page navigation test |

---

## 3. Required Railway Environment Variables

- **Frontend Service (`frontend/`):**
  - `VITE_API_BASE_URL=https://<your-backend-domain>.up.railway.app/api/v1` (now honored both at Docker build time and Nginx container startup)
- **Backend Service (`backend/`):**
  - `CORS_ORIGINS=https://<your-frontend-domain>.up.railway.app` *(optional on Railway `*.up.railway.app` / `*.vercel.app` when left unset, recommended explicitly for custom domains)*
  - `AUTO_SEED_ON_STARTUP=true`

---

## 4. Test & Verification Results

- **Backend Suite (`cd backend && python3 -m pytest tests -v`):** **23 passed, 0 failed** (`20.39s`, exit code `0`), including `test_cors_origins_normalization_and_railway_preflight` and `test_all_50_seeded_products_accessible_via_pagination` (all 5 pages, `total: 50`, `page_size: 12`, `total_pages: 5`).
- **Frontend Production Build (`cd frontend && npm run build`):** `tsc && vite build` passed (`2.15s`, exit code `0`).
- **Frontend Tests (`cd frontend && npm test -- --run`):** **8 passed, 0 failed** (`1.55s`, exit code `0`).
- **Nginx Runtime Env Script (`sh -n` + execution check):** Verified `docker-entrypoint-env.sh` emits valid `window.__GLOWCART_CONFIG__`.
- **Deployed Railway Verification:** **Pending** — deployed frontend/backend URLs and Railway CLI access are not present in this repository/host; changes must also be pushed/redeployed to Railway before live browser verification can run.
