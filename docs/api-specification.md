# API Specification — GlowCart (`/api/v1`)

Base URL: `/api/v1` · Interactive OpenAPI: `/docs`

## 1. Authentication & Addresses

| Method | Path | Auth | Role | Purpose |
|---|---|---|---|---|
| `POST` | `/auth/register` | Public | Any | Register customer account (`201`) |
| `POST` | `/auth/login` | Public | Any | Authenticate & issue access/refresh JWT (`200`) |
| `POST` | `/auth/refresh` | Refresh JWT | Any | Rotate refresh token & issue new access token (`200`) |
| `POST` | `/auth/logout` | Bearer JWT | Any | Revoke current access & refresh tokens (`200`) |
| `GET` | `/auth/me` | Bearer JWT | Any | Get authenticated user profile (`200`) |
| `PUT` | `/auth/me` | Bearer JWT | Any | Update own full name / phone (`200`) |
| `POST` | `/auth/forgot-password` | Public | Any | Generate time-limited reset token (`200`) |
| `POST` | `/auth/reset-password` | Public | Any | Consume reset token & update password (`200`) |
| `GET` | `/addresses` | Bearer JWT | Customer+ | List saved delivery addresses |
| `POST` | `/addresses` | Bearer JWT | Customer+ | Create delivery address (`201`) |
| `PUT` | `/addresses/{id}` | Bearer JWT | Owner | Update delivery address |
| `DELETE` | `/addresses/{id}` | Bearer JWT | Owner | Delete delivery address (`204`) |

## 2. Catalog, Categories, Brands & Variants

| Method | Path | Auth | Role | Purpose |
|---|---|---|---|---|
| `GET` | `/categories` | Public | Any | List active cosmetic categories |
| `POST` | `/admin/categories` | Bearer JWT | Admin+ | Create category (`201`) |
| `PUT` | `/admin/categories/{id}` | Bearer JWT | Admin+ | Update category |
| `GET` | `/brands` | Public | Any | List active cosmetic brands |
| `POST` | `/admin/brands` | Bearer JWT | Admin+ | Create brand (`201`) |
| `PUT` | `/admin/brands/{id}` | Bearer JWT | Admin+ | Update brand |
| `GET` | `/products` | Public | Any | Filter, sort, paginate products (`q`, `category_slug`, `brand_slug`, `min_price`, `max_price`, `in_stock`, `skin_type`, `shade`, `sort`, `page`, `page_size`) |
| `GET` | `/products/search` | Public | Any | Search products by keyword |
| `GET` | `/products/{id}` | Public | Any | Product details with variants, images, specs |
| `POST` | `/admin/products` | Bearer JWT | Admin+ | Create product (`201`) |
| `PUT` | `/admin/products/{id}` | Bearer JWT | Admin+ | Update product |
| `DELETE` | `/admin/products/{id}` | Bearer JWT | Admin+ | Archive product (`204`) |
| `POST` | `/admin/products/{id}/images` | Bearer JWT | Admin+ | Upload validated `.jpg/.png/.webp` image (`201`) |
| `GET` | `/products/{id}/variants` | Public | Any | List variants for product |
| `POST` | `/admin/variants` | Bearer JWT | Admin+ | Create variant SKU (`201`) |
| `PUT` | `/admin/variants/{id}` | Bearer JWT | Admin+ | Update variant |

## 3. Inventory & Batches

| Method | Path | Auth | Role | Purpose |
|---|---|---|---|---|
| `GET` | `/admin/inventory` | Bearer JWT | Admin+ | List variant stock summaries |
| `POST` | `/admin/inventory/batches` | Bearer JWT | Admin+ | Receive stock batch with manufacture/expiry dates (`201`) |
| `POST` | `/admin/inventory/adjustments` | Bearer JWT | Admin+ | Adjust stock with mandatory audit reason (`409` if negative) |
| `GET` | `/admin/inventory/low-stock` | Bearer JWT | Admin+ | List low/out-of-stock variants |
| `GET` | `/admin/inventory/expiring` | Bearer JWT | Admin+ | List expired & expiring-soon batches (`days` param) |
| `GET` | `/admin/inventory/movements` | Bearer JWT | Admin+ | Audit movement ledger (`RECEIVED`, `SOLD`, `RESERVED`, `RELEASED`, `ADJUSTED`) |

## 4. Cart, Wishlist, Promotions, Orders & Payments

| Method | Path | Auth | Role | Purpose |
|---|---|---|---|---|
| `GET` | `/cart` | Bearer JWT | Customer+ | Get cart + subtotal/discount/shipping/total (`?coupon_code=`) |
| `POST` | `/cart/items` | Bearer JWT | Customer+ | Add variant to cart (`409` if stock insufficient or expired) |
| `PUT` | `/cart/items/{id}` | Bearer JWT | Customer+ | Update item quantity |
| `DELETE` | `/cart/items/{id}` | Bearer JWT | Customer+ | Remove cart item |
| `GET` | `/wishlist` | Bearer JWT | Customer+ | List saved products |
| `POST` | `/wishlist/items` | Bearer JWT | Customer+ | Add product to wishlist (`201`) |
| `DELETE` | `/wishlist/items/{id}` | Bearer JWT | Customer+ | Remove wishlist item |
| `GET` | `/promotions` | Public | Any | List active promotions & coupon summaries |
| `POST` | `/admin/promotions` | Bearer JWT | Admin+ | Create promotion & optional coupon (`201`) |
| `GET` | `/admin/coupons` | Bearer JWT | Admin+ | List coupons |
| `POST` | `/admin/coupons` | Bearer JWT | Admin+ | Create coupon (`201`) |
| `POST` | `/orders` | Bearer JWT | Customer+ | Transactional checkout with snapshots & `idempotency_key` (`201`) |
| `GET` | `/orders` | Bearer JWT | Customer+ | List own orders |
| `GET` | `/orders/{id}` | Bearer JWT | Owner/Admin | Get order detail & snapshots |
| `POST` | `/orders/{id}/cancel` | Bearer JWT | Owner | Cancel eligible order & release stock |
| `GET` | `/admin/orders` | Bearer JWT | Admin+ | List all orders |
| `PATCH` | `/admin/orders/{id}/status` | Bearer JWT | Admin+ | Enforce valid state transition & FEFO deduction |
| `POST` | `/payments` | Bearer JWT | Owner | Create/retrieve payment intent (`201`) |
| `GET` | `/payments/{id}` | Bearer JWT | Owner/Admin | View payment & transactions |
| `POST` | `/payments/webhook` | HMAC Header | Provider | Verify `X-Webhook-Signature` & capture idempotently |
| `GET` | `/admin/payments` | Bearer JWT | Admin+ | List all payments |
| `POST` | `/admin/payments/{id}/refund` | Bearer JWT | Admin+ | Refund paid order (`200`) |

## 5. Reviews, Support, Notifications, Analytics & Super Admin

| Method | Path | Auth | Role | Purpose |
|---|---|---|---|---|
| `POST` | `/reviews` | Bearer JWT | Customer+ | Create review (`409` duplicate; auto verified-purchase check) |
| `GET` | `/products/{id}/reviews` | Public | Any | List approved product reviews |
| `PUT` | `/reviews/{id}` | Bearer JWT | Owner | Edit own review |
| `DELETE` | `/reviews/{id}` | Bearer JWT | Owner/Admin | Delete review (`204`) |
| `GET` | `/admin/reviews` | Bearer JWT | Admin+ | List all reviews for moderation |
| `PATCH` | `/admin/reviews/{id}/moderate` | Bearer JWT | Admin+ | Approve/hide review |
| `POST` | `/messages` | Bearer JWT | Customer+ | Submit customer support message (`201`) |
| `GET` | `/messages` | Bearer JWT | Customer/Admin | View own messages (or all as Admin) |
| `POST` | `/admin/messages/{id}/reply` | Bearer JWT | Admin+ | Reply & notify customer |
| `GET` | `/notifications` | Bearer JWT | Customer+ | List user notifications |
| `PATCH` | `/notifications/{id}/read` | Bearer JWT | Owner | Mark notification read |
| `GET` | `/admin/analytics/overview` | Bearer JWT | Admin+ | KPI card metrics |
| `GET` | `/admin/analytics/sales` | Bearer JWT | Admin+ | Revenue series (`daily`/`weekly`/`monthly`/`yearly`) |
| `GET` | `/admin/analytics/best-sellers` | Bearer JWT | Admin+ | Top-selling products |
| `GET` | `/admin/analytics/categories` | Bearer JWT | Admin+ | Sales by category & brand |
| `GET` | `/admin/analytics/variants` | Bearer JWT | Admin+ | Lipstick/foundation shades, color & volume analytics |
| `GET` | `/admin/analytics/inventory` | Bearer JWT | Admin+ | Inventory health summary |
| `GET` | `/admin/reports/export` | Bearer JWT | Admin+ | Download CSV (`sales` or `inventory`) |
| `GET` | `/admin/customers` | Bearer JWT | Admin+ | List user accounts |
| `POST` | `/admin/users` | Bearer JWT | Super Admin | Create admin/super_admin account (`201`) |
| `PATCH` | `/admin/users/{id}/role` | Bearer JWT | Super Admin | Assign role / active flag |
| `GET` | `/admin/roles` | Bearer JWT | Super Admin | List roles & permissions |
| `PUT` | `/admin/roles/{name}` | Bearer JWT | Super Admin | Update role permissions |
| `GET` | `/admin/audit-logs` | Bearer JWT | Super Admin | Inspect immutable audit logs |
| `GET` / `PUT` | `/admin/settings` | Bearer JWT | Admin / Super Admin | View or update store settings |

