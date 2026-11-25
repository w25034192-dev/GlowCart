# Latest Session Context — GlowCart

> **Updated:** 2026-11-25 (Session 2 — Docker Build Fix)
> **Current Focus:** Railway Docker build failure fixed (`COPY --chmod=755`); ready for push + redeploy

## What Was Fixed
1. **Runtime + Build-Time API URL Resolution & Normalization:**
   - Added [`frontend/src/utils/apiConfig.ts`](../frontend/src/utils/apiConfig.ts) (`resolveApiBaseUrl`, `API_BASE_URL`, `BACKEND_ORIGIN`) reading runtime `window.__GLOWCART_CONFIG__?.VITE_API_BASE_URL` first, then `import.meta.env.VITE_API_BASE_URL`, then `http://localhost:8000/api/v1`.
   - Normalized missing schemes, mixed-content `http://` -> `https://` on HTTPS pages, trailing slashes, duplicate `/api/v1/api/v1`, and missing `/api/v1` suffixes across `services/api.ts`, `utils/media.ts`, and `AdminOperationsPages.tsx`.
   - Added runtime `/env-config.js` generation in `frontend/docker-entrypoint-env.sh`, `frontend/Dockerfile`, `frontend/nginx.conf.template`, `frontend/index.html`, and `frontend/public/env-config.js`.
2. **Backend CORS Normalization & Railway Support:**
   - Updated [`backend/app/core/config.py`](../backend/app/core/config.py) and [`backend/app/main.py`](../backend/app/main.py) to strip quotes/trailing slashes from `CORS_ORIGINS`, support `FRONTEND_URL` / `PUBLIC_FRONTEND_URL` / `CORS_ORIGIN_REGEX`, and auto-allow HTTPS `*.up.railway.app` / `*.vercel.app` origins on Railway when `CORS_ORIGINS` is omitted.
3. **Catalog Error Diagnostics:**
   - [`frontend/src/pages/customer/CatalogPage.tsx`](../frontend/src/pages/customer/CatalogPage.tsx) now displays `API endpoint: ${API_BASE_URL}/products` inside the accessible `role="alert"` error box.

## Verified Checks
- `cd backend && python3 -m pytest tests -v`: **23 passed, 0 failed** (`20.39s`, exit code `0`), including `test_cors_origins_normalization_and_railway_preflight` and `test_all_50_seeded_products_accessible_via_pagination` (`total: 50`, `page: 1..5`, `page_size: 12`, `total_pages: 5`).
- `cd frontend && npm run build`: **passed** (`2.15s`, exit code `0`).
- `cd frontend && npm test -- --run`: **8 passed, 0 failed** (`1.55s`, exit code `0`).

## Remaining Before Task Closure
- Push updates and redeploy both Railway services (set `VITE_API_BASE_URL=https://<backend-domain>/api/v1` on the Railway frontend service and `CORS_ORIGINS=https://<frontend-domain>` on the Railway backend service).
- Test the live deployed frontend URL across All Products (all 5 pages / 50 products), Makeup, Skincare, Sun Care, Hair Care, Fragrance, and browser Network/Console tabs.
