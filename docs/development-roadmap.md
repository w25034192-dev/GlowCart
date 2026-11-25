# Development Roadmap — GlowCart

| Phase | Name | Key Deliverables | Verification Gate | Status |
|---|---|---|---|---|
| **1** | Repository Inspection & Planning | SRS, Architecture, DB Design, Mermaid Diagrams, Roadmap, Initial Status | Doc & Link Review | In Progress |
| **2** | Project Setup | Backend FastAPI skeleton, Frontend Vite/TS/Tailwind skeleton, `.env.example`, `docker-compose.yml` | Structure & Config Check | Pending |
| **3** | Database & Authentication | 27 SQLAlchemy models, Alembic initial migration, JWT + Argon2id/bcrypt auth, RBAC, Auth tests | Pytest Auth & RBAC | Pending |
| **4** | Catalog & Product Management | Categories, Brands, Products, Images, Variants, Search/Filter, Demo Seeder (8/15/50/100+), Admin CRUD | Pytest Catalog & RBAC | Pending |
| **5** | Inventory Management | Variant Stock, Batches & Expiry, Movements Ledger, Alerts, FEFO Allocation, Concurrency Safety | Pytest FEFO & Expiry | Pending |
| **6** | Customer Frontend | Storefront Home, Catalog, Category/Brand/Search, Product Details w/ Shade/Volume Selector, Auth Pages | Component & Route Review | Pending |
| **7** | Cart, Wishlist, Promotions & Checkout | Cart API/UI, Wishlist API/UI, Coupons & Promotions, Checkout Flow | Pytest Cart/Coupon | Pending |
| **8** | Orders & Payments | 9-State Order Workflow, Snapshots, COD, Sandbox Payment + Webhook Idempotency, Tracking | Pytest Orders/Webhooks | Pending |
| **9** | Reviews & Customer Service | Verified-Purchase Reviews, Customer Messages, Admin Replies, Notifications | Pytest Reviews/Support | Pending |
| **10** | Admin Dashboard & Analytics | Admin Sidebar, KPI Cards, Recharts Charts, SQL Analytics APIs, Report Exports | Pytest Analytics Accuracy | Pending |
| **11** | Security, Integration & Performance | Full Integration Suite, Concurrency Tests, Query Audit, Security & QA Verification | Pytest + Agent B/C Audit | Pending |
| **12** | Deployment & Final Documentation | Vercel/Railway Configs, API Spec, User/Install/Deploy Manuals, Academic Report, Viva | Final Release Gates | Pending |

