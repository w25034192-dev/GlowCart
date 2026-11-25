# Testing Report — GlowCart

> **Last Verified:** 2026-11-25  
> **Verification Environment:** Python `3.12.7`, `pytest 9.2.0`, SQLite test engine (`PRAGMA foreign_keys=ON`), FastAPI `TestClient`.

---

## 1. Executed Backend Test Suite (`pytest tests -v`)

**Command:** `cd backend && python3 -m pytest tests -v`  
**Exit Code:** `0`  
**Result:** **21 passed, 0 failed** (`19.45s`)

| Test Module | Test Case | Status | Verified Behavior |
|---|---|---|---|
| `test_auth_rbac.py` | `test_health_endpoint` | PASSED | `/health` returns `200` and service metadata |
| `test_auth_rbac.py` | `test_register_login_refresh_me_and_logout` | PASSED | Registration, duplicate `409`, JWT login, `/auth/me`, refresh rotation, logout revocation (`401` on replay) |
| `test_auth_rbac.py` | `test_forgot_and_reset_password` | PASSED | Reset token issuance, password change, old credential rejection |
| `test_auth_rbac.py` | `test_customer_cannot_access_admin_or_super_admin_endpoints` | PASSED | RBAC enforcement (`403` for customer/admin on super_admin route) |
| `test_auth_rbac.py` | `test_profile_and_address_crud` | PASSED | Profile update and address create/list/delete |
| `test_auth_rbac.py` | `test_production_settings_reject_default_secrets` | PASSED | Fail-closed guard rejects dev default JWT/webhook secrets in `production` |
| `test_auth_rbac.py` | `test_railway_postgres_url_normalization` | PASSED | Normalizes Railway `postgres://` and `postgresql://` URLs to `postgresql+psycopg://` |
| `test_catalog_inventory.py` | `test_catalog_crud_and_filtering` | PASSED | Admin CRUD, RBAC `403`, search, skin-type & price filtering, variants |
| `test_catalog_inventory.py` | `test_inventory_batches_expiry_and_fefo_allocation` | PASSED | Expired batch exclusion, negative-stock `409` rejection, FEFO earliest-expiry-first deduction |
| `test_catalog_inventory.py` | `test_product_image_upload_validation` | PASSED | Rejects `.exe` upload (`400 Bad Request`) |
| `test_catalog_inventory.py` | `test_demo_seeder_meets_minimum_catalog_counts` | PASSED | Verifies `>= 8` categories, `>= 15` brands, `>= 50` products, `>= 100` variants |
| `test_catalog_inventory.py` | `test_ensure_initial_data_seeds_when_empty_and_creates_default_admin` | PASSED | Seeds 50+ products across Makeup/Skincare/Sun Care/Hair Care/Fragrance + default admin when DB is empty; idempotent on repeat |
| `test_catalog_inventory.py` | `test_all_seeded_categories_and_skincare_endpoint_consistency` | PASSED | Verifies all 8 categories active, every category returns `> 0` matching products (`skincare`: 12), no duplicates, and trimmed/case-insensitive slug lookup |
| `test_catalog_inventory.py` | `test_ensure_initial_data_recovers_missing_skincare_when_other_products_exist` | PASSED | Seeds Skincare demo products idempotently when pre-existing non-skincare products exist without duplicating existing items |
| `test_orders_payments_cart.py` | `test_cart_wishlist_coupon_and_cod_order_snapshot` | PASSED | Wishlist, coupon `LIP10`, COD order, idempotency replay, price snapshot immutability, customer status `403` |
| `test_orders_payments_cart.py` | `test_sandbox_payment_and_duplicate_webhook_idempotency` | PASSED | Sandbox intent, HMAC-SHA256 webhook verification, duplicate `provider_event_id` deduplication |
| `test_orders_payments_cart.py` | `test_expired_batch_cannot_be_sold_and_no_overselling_last_unit` | PASSED | Expired batch blocked (`409`), 2 concurrent checkouts for last unit yield `[201, 409]` |
| `test_orders_payments_cart.py` | `test_cancel_processing_order_restores_fefo_batches_without_touching_other_reserved_stock` | PASSED | Cancelling finalized order restores FEFO batch & `available_quantity` with `RETURNED` movement without touching other orders' reservations |
| `test_reviews_support_analytics.py` | `test_reviews_permissions_verified_purchase_and_duplicates` | PASSED | Verified-purchase badge, duplicate `409`, non-owner edit/delete `403` |
| `test_reviews_support_analytics.py` | `test_customer_messages_admin_reply_and_notifications` | PASSED | Message creation, admin reply, notification dispatch |
| `test_reviews_support_analytics.py` | `test_analytics_excludes_cancelled_and_refunded_revenue` | PASSED | Cancelled orders excluded from `total_revenue` KPI and sales series |

---

## 2. Frontend Build & Test Status (`TypeScript`, `Vite`, `Vitest` + `React Testing Library`)
- **Build Command:** `cd frontend && npm run build` (`tsc && vite build`) — **PASSED** (`2.02s`, exit code `0`).
- **Test Command:** `cd frontend && npm test -- --run` (`vitest run`) — **6 passed, 0 failed** (`1.41s`, exit code `0`):
  - Homepage hero, featured categories, best sellers, skin-routine builder, and testimonials render (`/`).
  - Unauthenticated redirect away from protected `/admin` routes.
  - Product shade variant selection updates SKU and price (`/products/prod-1`).
  - Skincare category loads products and resets stale keyword filters when navigating from `/category/makeup` -> `/category/skincare`.
  - All 8 seeded category routes (`/category/makeup`, `/category/skincare`, `/category/sun-care`, `/category/hair-care`, `/category/body-care`, `/category/fragrance`, `/category/beauty-tools`, `/category/makeup-sets`) request their exact `category_slug` and display products.
  - API failure shows `role="alert"` error message with `Retry` button instead of `"0 products available"`.

---

## 3. PostgreSQL Migration & Runtime Notes
- Alembic initial migration (`backend/alembic/versions/9d984bd1e8dc_initial_schema.py`) was autogenerated and executed cleanly (`alembic upgrade head`, exit code `0`) against SQLite; live `uvicorn` + `vite preview` verified all 8 categories (`200 OK`, CORS headers present) with zero backend errors. Live Railway PostgreSQL and Chrome DevTools remote debugging were not reachable from this host.

