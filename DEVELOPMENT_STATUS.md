# Development Status — GlowCart

> **Last Updated:** 2026-11-25  
> **Overall Status:** Backend API, 27-Table Schema, React Frontend, and Full Documentation Implemented; Independent Verification Remediated  

---

## Acceptance & Environment Status

| Area | Status | Notes / Evidence |
|---|---|---|
| **27-Table DB & Alembic** | Completed | `backend/app/models/*`, `backend/alembic/versions/9d984bd1e8dc_initial_schema.py` |
| **Auth, JWT, Argon2id/bcrypt & RBAC** | Completed | `backend/app/api/v1/auth.py`, `super_admin.py`, `tests/test_auth_rbac.py` |
| **Catalog, Variants & Seeder** | Completed | 8 categories, 20 brands, 50 products, 120+ variants (`app/db/seed.py`); case-insensitive category slug matching + Skincare partial-DB recovery verified |
| **FEFO Inventory & Batches** | Completed | Expiry blocking, FEFO deduction & cancel restocking (`tests/test_catalog_inventory.py`) |
| **Cart, Wishlist, Orders & Payments** | Completed | Snapshots, idempotency, concurrency lock, HMAC webhook (`tests/test_orders_payments_cart.py`) |
| **Reviews, Support & Analytics** | Completed | Verified reviews, messages/notifications, SQL KPIs & CSV (`tests/test_reviews_support_analytics.py`) |
| **React + TypeScript + Tailwind Frontend** | Completed & Built | Complete pages, stores, Recharts dashboard, filter-sync & error-UI fix (`CatalogPage.tsx`), `tsc && vite build` clean (`2.02s`), Vitest **6 passed, 0 failed** |
| **Documentation & Academic Report** | Completed | `README.md`, `docs/*.md`, `docs/skincare-category-fix.md`, `docs/diagrams/*.mmd`, `docs/final-project-report.md` |

## Known Limitations & Environment Blockers
1. Chrome remote debugging (`DevToolsActivePort`) was unavailable on this host, so automated live Chrome DevTools console inspection was skipped; live HTTP routes (`/category/*`, `/images/catalog/*.svg`) and backend `uvicorn` responses across all 8 categories were verified directly (`200 OK`).
2. `argon2-cffi`, `psycopg`, and a local `glowcart` PostgreSQL database are absent on this host (`Postgres.app` holds unrelated DBs); backend tests execute against SQLite transactions with bcrypt fallback, while `requirements.txt` and `backend/Dockerfile` target PostgreSQL + Argon2id on Railway.
