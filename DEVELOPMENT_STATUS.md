# Development Status — GlowCart

> **Last Updated:** 2026-11-25  
> **Overall Status:** Backend API, 27-Table Schema, React Frontend, and Full Documentation Implemented; Independent Verification Remediated  

---

## Acceptance & Environment Status

| Area | Status | Notes / Evidence |
|---|---|---|
| **27-Table DB & Alembic** | Completed | `backend/app/models/*`, `backend/alembic/versions/9d984bd1e8dc_initial_schema.py` |
| **Auth, JWT, Argon2id/bcrypt & RBAC** | Completed | `backend/app/api/v1/auth.py`, `super_admin.py`, `tests/test_auth_rbac.py` |
| **Catalog, Variants & Seeder** | Completed | 8 categories, 20 brands, 50 products, 120+ variants (`app/db/seed.py`) |
| **FEFO Inventory & Batches** | Completed | Expiry blocking, FEFO deduction & cancel restocking (`tests/test_catalog_inventory.py`) |
| **Cart, Wishlist, Orders & Payments** | Completed | Snapshots, idempotency, concurrency lock, HMAC webhook (`tests/test_orders_payments_cart.py`) |
| **Reviews, Support & Analytics** | Completed | Verified reviews, messages/notifications, SQL KPIs & CSV (`tests/test_reviews_support_analytics.py`) |
| **React + TypeScript + Tailwind Frontend** | Authored (Unbuilt) | Complete pages, stores, Recharts dashboard & Vitest specs; `npm test` / `vite build` pending Node.js 20+ |
| **Documentation & Academic Report** | Completed | `README.md`, `docs/*.md`, `docs/diagrams/*.mmd`, `docs/final-project-report.md` |

## Known Limitations & Environment Blockers
1. `node` and `npm` are not installed in this environment, so `frontend/` Vitest tests and `vite build` have not been executed locally.
2. `argon2-cffi`, `psycopg`, and an active PostgreSQL daemon are absent in the offline sandbox; backend tests execute against SQLite transactions with bcrypt fallback, while `requirements.txt` and `.env.example` target PostgreSQL + Argon2id in deployment.
