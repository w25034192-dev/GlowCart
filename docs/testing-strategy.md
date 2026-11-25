# Testing Strategy — GlowCart

## 1. Testing Objectives

Verify correctness, transactional safety, security boundaries (RBAC, JWT, payment verification), FEFO expiry enforcement, concurrency safety, and frontend UI/UX compliance before delivery.

## 2. Testing Levels & Tooling

- **Backend Unit & Integration Tests (`Pytest` + `httpx` / FastAPI `TestClient`):**
  - Auth lifecycle (register, login, refresh, logout, forgot/reset password, RBAC enforcement).
  - Catalog, categories, brands, variants, search/filter/pagination.
  - Inventory FEFO allocation, expired batch blocking, negative-stock prevention, movement audit records.
  - Concurrency test: simultaneous checkout against final available unit ensures zero overselling.
  - Cart, coupon validation, checkout snapshots (catalog price changes do not alter historical orders).
  - Payments & duplicate webhook idempotency.
  - Reviews (verified purchase, edit/delete ownership, duplicate review prevention) and support messages.
  - Analytics accuracy (cancelled/refunded orders excluded from net revenue).
- **Frontend Tests (`Vitest` + `React Testing Library`):**
  - Navigation, login/register forms, protected admin routes, catalog filters, variant shade/volume selector, cart/checkout flow, admin pages.
- **Security & Performance Checks:**
  - Input validation (422), unauthorized/forbidden (401/403), SQLi/XSS protection via ORM/escaping, query count / N+1 checks, endpoint latency measurements under local test conditions.

## 3. Acceptance Test Matrix (To Be Populated Only With Executed Results)

| Test ID | Scenario | Preconditions | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| **TC-001** | Customer cannot access `/api/v1/admin/*` | Authenticated customer JWT | HTTP `403 Forbidden` | Pending execution | Pending |
| **TC-002** | Expired batch cannot be sold | Variant has only expired batch | Checkout rejected (`409 Conflict`) | Pending execution | Pending |
| **TC-003** | Stock cannot become negative | Variant stock = 1 | Adjustment/checkout below 0 rejected | Pending execution | Pending |
| **TC-004** | Simultaneous purchases of last unit | Variant stock = 1; 2 concurrent requests | 1 succeeds, 1 fails (`409`); stock = 0 | Pending execution | Pending |
| **TC-005** | Duplicate payment webhook | Order in `PAYMENT_PENDING` | 1 payment transaction created; replay ignored | Pending execution | Pending |
| **TC-006** | Cancelled/refunded orders in revenue | Paid, cancelled, and refunded orders exist | Net revenue excludes cancelled/refunded | Pending execution | Pending |
| **TC-007** | Historical order price snapshot | Order placed, variant price updated later | Order item keeps purchase price & SKU | Pending execution | Pending |

