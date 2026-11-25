# Presentation Outline — GlowCart Final Year Project

1. **Slide 1: Title & Identity** — GlowCart: Cosmetic E-Commerce, FEFO Inventory & Sales Analytics.
2. **Slide 2: Problem Statement** — Challenges of generic e-commerce for cosmetics (shade/volume SKUs, expired stock risks, overselling, inaccurate revenue reporting).
3. **Slide 3: Objectives & Scope** — Three roles (Customer, Admin, Super Admin), USD base pricing, 27 relational tables.
4. **Slide 4: System Architecture** — React + TypeScript + Vite (Vercel) → FastAPI `/api/v1` (Railway) → PostgreSQL + Alembic.
5. **Slide 5: Database & Cosmetic Variant Modeling** — Separate `products`, `product_variants`, `inventory`, `inventory_batches`, `inventory_movements`, and order snapshots.
6. **Slide 6: FEFO Inventory & Concurrency Control** — Blocking expired batches, row-level locking, and transaction-safe stock reservation/deduction.
7. **Slide 7: Order Lifecycle & Payment Idempotency** — 9 order statuses, COD vs. HMAC-signed Sandbox webhook, duplicate event protection.
8. **Slide 8: Admin Analytics Dashboard** — Recharts KPIs, daily/weekly/monthly/yearly revenue, category/brand & lipstick/foundation shade analytics.
9. **Slide 9: Security & Testing Results** — RBAC enforcement, 15/15 passing backend Pytest cases, honest limitations.
10. **Slide 10: Conclusion & Future Work** — Summary, live payment gateway & multi-currency roadmap.

