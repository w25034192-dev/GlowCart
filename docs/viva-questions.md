# Viva Questions & Technical Answers — GlowCart

1. **Why separate `inventory`, `inventory_batches`, and `inventory_movements` instead of a single `stock` column on `products`?**  
   Cosmetic items vary by shade and volume (`product_variants`) and arrive in batches with distinct manufacture and expiry dates (`inventory_batches`). Separating `inventory` (variant totals) from `inventory_batches` enables FEFO allocation and expiry blocking, while `inventory_movements` provides an immutable audit trail (`RECEIVED`, `SOLD`, `RESERVED`, `RELEASED`, `ADJUSTED`).

2. **How does GlowCart prevent overselling the last unit under concurrent checkouts?**  
   Order creation executes inside an atomic database transaction with row locking (`SELECT ... FOR UPDATE` on PostgreSQL, serialized transaction lock in SQLite) inside `InventoryService.reserve_stock`. The first transaction reserves the unit (`available_quantity` decreases, `reserved_quantity` increases); the second transaction reads zero sellable stock and fails cleanly with `409 Conflict`.

3. **How are historical orders protected if an administrator later changes a product's price or name?**  
   `order_items` persists `product_name_snapshot`, `variant_sku_snapshot`, `variant_label_snapshot`, `unit_price`, and `line_total` at purchase time, and `orders` stores `shipping_address_snapshot` as JSON. Subsequent catalog or address edits never mutate historical orders.

4. **How is duplicate payment webhook delivery handled?**  
   `payment_transactions.provider_event_id` has a database `UNIQUE` constraint. Before capturing payment, `PaymentService.process_webhook` verifies the HMAC-SHA256 `X-Webhook-Signature` header and checks whether `provider_event_id` has already been processed; replays return `200 OK` with `duplicate: true` without re-deducting stock or duplicating ledger rows.

5. **How is Role-Based Access Control (RBAC) enforced?**  
   Every administrative route uses FastAPI's `Depends(require_roles("admin", "super_admin"))` or `Depends(require_roles("super_admin"))`, validating the JWT signature, token type (`access`), active status, and database role server-side rather than relying solely on frontend route guards.

6. **How do revenue analytics handle cancelled and refunded orders?**  
   `AnalyticsService` explicitly filters out orders with status `CANCELLED` or `REFUNDED` (`NON_REVENUE_STATUSES`) when computing `total_revenue`, revenue time-series, category/brand sales, and best sellers.

