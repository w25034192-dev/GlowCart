# Database Design — GlowCart

## 1. Database Overview

GlowCart uses **PostgreSQL** with **SQLAlchemy 2.0** and **Alembic** migrations. The schema comprises **27 normalized tables** using `UUID` primary keys, `NUMERIC(12, 2)` for all monetary amounts, `DateTime(timezone=True)` audit timestamps, foreign-key integrity, unique constraints, check constraints, and targeted B-tree indexes.

## 2. Core Tables Summary (27 Tables)

| # | Table | Primary Key | Purpose & Key Constraints |
|---|---|---|---|
| 1 | `roles` | `id (UUID)` | System roles (`customer`, `admin`, `super_admin`), unique `name`, JSON `permissions`. |
| 2 | `users` | `id (UUID)` | User accounts, unique `email`, `password_hash`, `role_id` FK, `is_active`, `reset_token_hash`. |
| 3 | `addresses` | `id (UUID)` | Customer delivery addresses, `user_id` FK (`CASCADE`), `is_default`. |
| 4 | `categories` | `id (UUID)` | Cosmetic categories/subcategories, unique `slug`, self-referential `parent_id` FK (`SET NULL`). |
| 5 | `brands` | `id (UUID)` | Cosmetic brands, unique `slug` & `name`, `country_of_origin`, `is_featured`. |
| 6 | `products` | `id (UUID)` | Product master records, `category_id` FK, `brand_id` FK, unique `slug`, `skin_types` JSON, `verified_ingredients`, `is_demo`. |
| 7 | `product_images` | `id (UUID)` | Product gallery images, `product_id` FK (`CASCADE`), `is_primary`, `sort_order`. |
| 8 | `product_variants` | `id (UUID)` | Shade/volume/size SKUs, `product_id` FK (`CASCADE`), unique `sku`, `shade_name`, `shade_code`, `color_name`, `hex_color`, `volume_ml`, `weight_g`, `size`, `price > 0`, `original_price`. |
| 9 | `inventory` | `id (UUID)` | 1:1 stock summary per variant (`variant_id` unique FK), `available_quantity >= 0`, `reserved_quantity >= 0`, `low_stock_threshold >= 0`. |
| 10 | `inventory_batches` | `id (UUID)` | Cosmetic batch & expiry tracking, `variant_id` FK, unique `(variant_id, batch_number)`, `manufacture_date`, `expiry_date`, `initial_quantity >= 0`, `remaining_quantity >= 0`. |
| 11 | `inventory_movements` | `id (UUID)` | Immutable stock movement ledger (`RECEIVED`, `SOLD`, `ADJUSTED`, `RETURNED`, `RESERVED`, `RELEASED`), `variant_id` FK, optional `batch_id` FK, `actor_id` FK, `quantity_delta`, `reason`. |
| 12 | `carts` | `id (UUID)` | 1:1 active shopping cart per user (`user_id` unique FK `CASCADE`). |
| 13 | `cart_items` | `id (UUID)` | Cart line items, `cart_id` FK (`CASCADE`), `variant_id` FK (`CASCADE`), unique `(cart_id, variant_id)`, `quantity > 0`. |
| 14 | `wishlists` | `id (UUID)` | 1:1 wishlist per user (`user_id` unique FK `CASCADE`). |
| 15 | `wishlist_items` | `id (UUID)` | Saved wishlist products, `wishlist_id` FK (`CASCADE`), `product_id` FK (`CASCADE`), unique `(wishlist_id, product_id)`. |
| 16 | `orders` | `id (UUID)` | Customer orders, unique `order_number`, unique `idempotency_key`, `user_id` FK, `status` (9 states), `payment_method`, `payment_status`, `subtotal`, `discount_amount`, `shipping_fee`, `total_amount`, `shipping_address_snapshot` JSON. |
| 17 | `order_items` | `id (UUID)` | Immutable order lines, `order_id` FK (`CASCADE`), `variant_id` FK (`SET NULL`), `product_name_snapshot`, `variant_sku_snapshot`, `variant_label_snapshot`, `unit_price`, `quantity > 0`, `line_total`. |
| 18 | `payments` | `id (UUID)` | Payment record per order, `order_id` unique/indexed FK, `method`, `provider`, `status`, `amount >= 0`, `currency`. |
| 19 | `payment_transactions` | `id (UUID)` | Gateway/webhook transaction audit log, `payment_id` FK (`CASCADE`), unique `provider_event_id`, `transaction_type`, `status`, `raw_payload` JSON. |
| 20 | `promotions` | `id (UUID)` | Storefront promotional campaigns, `title`, `discount_type`, `discount_value`, `starts_at`, `ends_at`, `is_active`. |
| 21 | `coupons` | `id (UUID)` | Discount coupon codes, unique `code`, `discount_type`, `discount_value`, `min_order_amount`, `max_uses`, `used_count >= 0`, `expires_at`. |
| 22 | `coupon_usages` | `id (UUID)` | Per-user/order coupon redemption log, `coupon_id` FK, `user_id` FK, `order_id` FK, unique `(coupon_id, order_id)`. |
| 23 | `reviews` | `id (UUID)` | Product reviews, `product_id` FK, `user_id` FK, unique `(product_id, user_id)`, `rating` (1–5), `is_verified_purchase`, `is_approved`. |
| 24 | `customer_messages` | `id (UUID)` | Customer support tickets, `user_id` FK, `subject`, `message`, `status` (`OPEN`, `IN_PROGRESS`, `RESOLVED`, `CLOSED`). |
| 25 | `message_replies` | `id (UUID)` | Threaded replies on support messages, `message_id` FK (`CASCADE`), `sender_id` FK, `body`, `is_admin_reply`. |
| 26 | `notifications` | `id (UUID)` | User notifications (order updates, replies, low-stock alerts), `user_id` FK (`CASCADE`), `title`, `body`, `is_read`. |
| 27 | `audit_logs` | `id (UUID)` | Immutable security & admin action trail, `actor_id` FK (`SET NULL`), `action`, `resource_type`, `resource_id`, `details` JSON, `ip_address`. |

## 3. Relationships Summary

- **One-to-One:** `product_variants ↔ inventory` (1:1), `users ↔ carts` (1:1), `users ↔ wishlists` (1:1), `orders ↔ payments` (1:1).
- **One-to-Many:** `roles → users`, `users → addresses`, `categories → categories` (self-parent), `categories → products`, `brands → products`, `products → product_images`, `products → product_variants`, `product_variants → inventory_batches`, `product_variants → inventory_movements`, `carts → cart_items`, `wishlists → wishlist_items`, `users → orders`, `orders → order_items`, `payments → payment_transactions`, `users → reviews`, `products → reviews`, `users → customer_messages`, `customer_messages → message_replies`, `users → notifications`, `users → audit_logs`.
- **Many-to-Many (via Join/Redemption Tables):** `carts ↔ product_variants` via `cart_items`; `wishlists ↔ products` via `wishlist_items`; `coupons ↔ orders` via `coupon_usages`.

## 4. Entity Relationship Diagram

See [`docs/diagrams/er-diagram.mmd`](./diagrams/er-diagram.mmd) for the complete Mermaid ERD covering all 27 tables.

## 5. Migration Instructions

```bash
cd backend
alembic upgrade head
```

Schema modifications must always be generated via `alembic revision --autogenerate -m "description"` and never by `Base.metadata.create_all()` in production.

