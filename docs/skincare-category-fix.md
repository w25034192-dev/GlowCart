# Skincare Category "0 Products Available" — Investigation, Root Causes, Fixes & Test Results

> **Date:** 2026-11-25  
> **Scope:** PostgreSQL/SQLAlchemy catalog relationships, FastAPI `/api/v1/categories` & `/api/v1/products`, startup seeding (`app/db/seed.py`), and React `CatalogPage` / `CustomerLayout` routing & filtering.

---

## 1. Investigation Summary

1. **Local & Deployment Database Check**
   - Checked local `Postgres.app` (`localhost:5432`): only unrelated databases exist locally (`postgres`, `winsandar`, `db_name`, `my_project`, `my_project_db`, `project_db`, `student`); no `glowcart` database or `backend/.env` exists locally (the empty DB originally reported was on Railway).
   - Verified `backend/alembic/versions/9d984bd1e8dc_initial_schema.py` and `backend/app/models/catalog.py`: `Product.category_id` is a non-null foreign key to `categories.id` (`ON DELETE RESTRICT`), with `Category.products` / `Product.category` SQLAlchemy relationships.
   - Executed `alembic upgrade head` + FastAPI lifespan auto-seed (`AUTO_SEED_ON_STARTUP=true`) against a fresh verification database: verified all **8 categories** and **50 products** (including **12 active Skincare products**) populate cleanly with zero duplicates.
2. **Backend API & Query Inspection (`/api/v1/categories`, `/api/v1/products`)**
   - Inspected `backend/app/api/v1/catalog.py` and `backend/app/services/catalog_service.py`:
     - `CatalogService.list_categories()` filters `Category.is_active.is_(True)`.
     - `CatalogService.list_products()` previously checked exact case-sensitive `Category.slug == category_slug` and `Brand.slug == brand_slug` without whitespace trimming, lowercase normalization, or checking `Category.is_active`.
   - Inspected `backend/app/db/seed.py`:
     - `CATEGORIES_DATA` defines `("Skincare", "skincare", ..., 2)` and `CATALOG_BLUEPRINT` defines **12 Skincare products** (`is_active=True`, `is_archived=False`, 24 volume variants, non-expired `InventoryBatch` records, `/images/catalog/skincare.svg`).
     - `ensure_initial_data()` previously only seeded when `db.query(Product).count() == 0`. If an existing database already contained a non-skincare product (e.g., manual test data) but `0` Skincare products, auto-seed skipped Skincare completely. Additionally, `seed_demo_data()` matched `Category` / `Brand` strictly by exact slug rather than case-insensitive `slug` or `name`, and did not reactivate `is_active=False` categories.
3. **Frontend Inspection (`CatalogPage.tsx`, `CustomerLayout.tsx`, Vitest setup)**
   - Inspected `frontend/src/pages/customer/CatalogPage.tsx`:
     - **Root Cause 1 (Stale State Across Category Route Transitions):** `CatalogPage` stored `q`, `selectedCategory`, `selectedBrand`, `skinType`, `shade`, `minPrice`, `maxPrice`, `inStockOnly`, `sort`, and `page` in `useState`, without syncing them via `useEffect` when `categorySlug`, `brandSlug`, or URL `searchParams` changed. Navigating from `/category/makeup` (with keyword/brand/price filters or `page > 1`) to `/category/skincare` kept stale filters active and caused `GET /api/v1/products?category_slug=skincare&...` to return `0` matching items.
     - **Root Cause 2 (Silent API Failure Masking as `"0 products available"`):** `useQuery` destructured only `{ data, isLoading }`, ignoring `isError`, `error`, and `refetch`. Any unreachable backend, CORS mismatch, or 5xx response rendered `"0 products available"` with no error message.
     - **Root Cause 3 (Category Heading Fallback & Reset):** Heading used `categorySlug?.replace('-', ' ')` instead of the authoritative `Category.name`, and there was no `"Reset Filters"` / `"Clear Filters"` action.
   - Inspected `frontend/vitest.config.ts` (was `0` bytes, blocking `npm test`) and `frontend/src/test/setup.ts` (needed `localStorage` fallback for Node runtime `--localstorage-file` warning under jsdom).
   - Inspected `frontend/src/layouts/CustomerLayout.tsx`: mobile drawer menu omitted `Sun Care`, `Hair Care`, and `Fragrance` links that existed on desktop.

---

## 2. Implemented Fixes (Zero Duplicate Products, PostgreSQL Source of Truth Preserved)

1. **`backend/app/services/catalog_service.py`**
   - Normalized `category_slug` and `brand_slug` (`strip().lower()`) and filtered with `func.lower(Category.slug) == normalized_category_slug` (`Category.is_active.is_(True)`) and `func.lower(Brand.slug) == normalized_brand_slug` (`Brand.is_active.is_(True)`).
2. **`backend/app/db/seed.py`**
   - Extracted `_ensure_categories_and_brands()` (case-insensitive lookup by `slug` or `name`, reactivates inactive records without duplicating) and `_seed_blueprint_entries()` (skips existing `Product.slug`, preserves deterministic SKU/batch numbering).
   - Updated `ensure_initial_data()` so it seeds the full catalog when `products` is empty, and idempotently seeds Skincare demo entries from `CATALOG_BLUEPRINT` if non-skincare products exist while Skincare has `0` products.
3. **`frontend/src/pages/customer/CatalogPage.tsx`**
   - Added `useEffect` resetting filter/pagination state when `categorySlug`, `brandSlug`, or `searchParams` change.
   - Normalized `activeCategorySlug` / `activeBrandSlug`, resolved `activeCategory?.name` for headings, added `Reset Filters` / `Clear Filters` controls, and rendered an accessible `role="alert"` error card with a `Retry` button whenever `isError` is true.
4. **`frontend/src/layouts/CustomerLayout.tsx`**
   - Added `Sun Care`, `Hair Care`, and `Fragrance` links to the mobile navigation menu alongside `Makeup` and `Skincare`.
5. **Test Infrastructure & TDD Coverage**
   - Restored `frontend/vitest.config.ts` and added an in-memory `localStorage` fallback in `frontend/src/test/setup.ts`.
   - Added backend tests (`test_all_seeded_categories_and_skincare_endpoint_consistency`, `test_ensure_initial_data_recovers_missing_skincare_when_other_products_exist`) in `backend/tests/test_catalog_inventory.py`.
   - Added frontend tests in `frontend/src/test/App.test.tsx` covering `/category/skincare`, route navigation filter reset, all 8 category pages, and API error alert rendering.

---

## 3. Verified Test & Runtime Results

- **Backend Test Suite (`cd backend && python3 -m pytest tests -v`):**
  - **Result:** **21 passed, 0 failed** (`19.45s`, exit code `0`), including all 8 category endpoints (`makeup`, `skincare`, `sun-care`, `hair-care`, `body-care`, `fragrance`, `beauty-tools`, `makeup-sets`), case-insensitive/trimmed slug matching, and partial-DB skincare recovery.
- **Frontend TypeScript & Production Build (`cd frontend && npm run build`):**
  - **Result:** `tsc && vite build` passed cleanly (**exit code `0`**, built in `2.02s`).
- **Frontend Automated Tests (`cd frontend && npm test -- --run`):**
  - **Result:** **6 passed, 0 failed** (`1.41s`, exit code `0`).
- **Live Server & Endpoint Verification (`alembic upgrade head` + `uvicorn` + `vite preview`):**
  - `GET /api/v1/categories` returned **8 active categories** (`200 OK`).
  - `GET /api/v1/products?category_slug=<slug>&page=1&page_size=50` returned `200 OK` with `Access-Control-Allow-Origin: http://localhost:5173` and exact counts:
    - `makeup`: `12` products
    - `skincare`: `12` products
    - `sun-care`: `5` products
    - `hair-care`: `5` products
    - `body-care`: `4` products
    - `fragrance`: `4` products
    - `beauty-tools`: `4` products
    - `makeup-sets`: `4` products
  - All 8 `/category/<slug>` preview routes and `/images/catalog/<slug>.svg` assets returned HTTP `200 OK`. Backend `uvicorn` logs showed zero errors or tracebacks.
- **Not Executed / Environment Constraints:**
  - Live Chrome DevTools browser session could not attach (`DevToolsActivePort` missing — Chrome remote debugging not active on host), and remote Railway PostgreSQL was not directly queried from this environment.

---

## 4. Next Session Context

- **Current Status:** All backend, database seeding, API category filtering, and React `CatalogPage` fixes are implemented and verified (`21 passed` pytest, `6 passed` Vitest, `tsc && vite build` green, live `uvicorn` + `vite preview` returning `200 OK` across all 8 categories).
- **Recommended Follow-Up on Railway / Browser:**
  - Verify Railway's `VITE_API_BASE_URL` build argument points to the deployed backend `/api/v1` URL and backend `AUTO_SEED_ON_STARTUP=true` is enabled (check Railway backend startup logs for `"GlowCart database was empty; auto-seeded demo catalog and default admin."`).
  - Open `/category/skincare` and sibling categories in Chrome and confirm `12 products available` (and zero console/network errors).
