# Use Cases — GlowCart

## UC-01: Customer Registration & Login
- **Actor:** Customer
- **Preconditions:** User has a valid email address and is not banned/inactive.
- **Main Flow:**
  1. Customer submits registration form (`email`, `full_name`, `password`).
  2. Backend validates input, hashes password, assigns `customer` role, creates user + cart + wishlist.
  3. Customer logs in with email/password and receives `access_token` and `refresh_token`.
- **Alternative Flow:** Duplicate email returns `409 Conflict`; invalid credentials return `401 Unauthorized`.
- **Postconditions:** Authenticated session established; user action recorded in `audit_logs`.

## UC-02: Dynamic Variant Selection & Add to Cart
- **Actor:** Customer
- **Preconditions:** Product and active variant exist with available non-expired stock.
- **Main Flow:**
  1. Customer opens product detail page and selects a shade swatch or volume chip.
  2. UI updates SKU, price, original price, discount, and stock badge.
  3. Customer clicks "Add to Cart" (`POST /api/v1/cart/items`).
- **Alternative Flow:** Requested quantity exceeds available stock -> `409 Conflict` / inline warning.
- **Postconditions:** `cart_items` row created or incremented.

## UC-03: Transactional Checkout & FEFO Allocation
- **Actor:** Customer
- **Preconditions:** Authenticated customer with non-empty cart and saved/new delivery address.
- **Main Flow:**
  1. Customer selects address, optional coupon, and payment method (`COD` or `SANDBOX`), then confirms checkout with an `idempotency_key`.
  2. Backend locks variant `inventory` and non-expired `inventory_batches` ordered by earliest `expiry_date` (FEFO).
  3. Server recalculates subtotal, coupon discount, shipping, and total.
  4. Backend creates `orders` (with address snapshot), `order_items` (with SKU/name/price snapshots), `payments`, reserves/deducts stock, logs `inventory_movements`, and clears cart.
- **Alternative Flow:** Repeated `idempotency_key` returns existing order (`200`/`201` idempotent replay); insufficient non-expired stock aborts transaction (`409 Conflict`).
- **Postconditions:** Order persisted with snapshots; stock cannot become negative.

## UC-04: Payment Webhook Verification
- **Actor:** Payment Sandbox Provider
- **Preconditions:** Order and `payments` record exist in `PAYMENT_PENDING` state.
- **Main Flow:**
  1. Provider posts signed webhook to `POST /api/v1/payments/webhook` with `provider_event_id`.
  2. Backend verifies HMAC signature and checks `payment_transactions` for duplicate `provider_event_id`.
  3. Backend updates `payments.status = PAID`, `orders.status = PAID`, and deducts reserved stock via FEFO.
- **Alternative Flow:** Duplicate `provider_event_id` returns `200 OK` without creating duplicate records or re-deducting stock.
- **Postconditions:** Order paid and stock finalized idempotently.

## UC-05: Admin Batch Stock Receipt & Expiry Enforcement
- **Actor:** Admin
- **Preconditions:** Authenticated `admin` or `super_admin`.
- **Main Flow:**
  1. Admin submits batch adjustment/receipt with `batch_number`, `manufacture_date`, `expiry_date`, `quantity_delta`, and `reason`.
  2. Backend creates/updates `inventory_batches`, updates `inventory.available_quantity`, and writes `inventory_movements`.
- **Alternative Flow:** Expired batches (`expiry_date <= today`) are excluded from sellable FEFO allocation and flagged in `/admin/inventory/expiring`.
- **Postconditions:** Complete batch traceability and audit trail maintained.

## UC-06: Admin Sales & Variant Analytics
- **Actor:** Admin
- **Preconditions:** Orders and inventory records exist in PostgreSQL.
- **Main Flow:** Admin opens Analytics dashboard; backend aggregates KPI metrics, revenue time-series, category/brand breakdowns, and shade/volume sales excluding `CANCELLED` and `REFUNDED` revenue.
- **Postconditions:** Accurate SQL-computed analytics rendered in Recharts.

## UC-07: Super Admin Role & Audit Management
- **Actor:** Super Admin
- **Preconditions:** Authenticated `super_admin`.
- **Main Flow:** Super Admin creates admin account, updates user roles/permissions, updates settings, or queries `audit_logs`.
- **Alternative Flow:** Non-super-admin receives `403 Forbidden`.
- **Postconditions:** RBAC changes logged in `audit_logs`.

