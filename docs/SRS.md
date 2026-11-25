# Software Requirements Specification (SRS) — GlowCart

> **Academic Project Title:** Design and Development of an International Web-Based Cosmetic E-Commerce and Inventory Management System with Sales Analytics  
> **Version:** 1.0.0  
> **Base Currency:** USD  

---

## 1. Introduction

GlowCart is an international cosmetic e-commerce platform paired with batch-aware inventory management and sales analytics. This Software Requirements Specification (SRS) defines the functional, non-functional, interface, and operational requirements for the GlowCart system.

## 2. Purpose

The purpose of this SRS is to establish an unambiguous contract for the engineering, verification, documentation, and academic evaluation of GlowCart across its three user roles: Customer, Admin, and Super Admin.

## 3. Project Scope

GlowCart encompasses:
- A responsive customer storefront (`React + TypeScript + Vite + Tailwind CSS`) for cosmetic product discovery, shade/volume variant selection, cart/wishlist management, coupon application, checkout (Cash on Delivery and Online Payment Sandbox), order tracking, product reviews, notifications, and customer support messaging.
- A RESTful API backend (`Python FastAPI + SQLAlchemy 2.0 + Alembic + PostgreSQL`) enforcing JWT authentication, Argon2id (with environment-verified bcrypt fallback only when Argon2id C extension is absent) password hashing, server-side RBAC, transactional FEFO batch inventory allocation, idempotent order/payment processing, and SQL-backed analytics.
- An Admin & Super Admin dashboard with Recharts analytics, catalog/variant management, batch/expiry tracking, order/payment operations, moderation, audit logging, and CSV report exports.

## 4. Intended Users

- **Customers:** International shoppers browsing cosmetics, filtering by category/brand/shade/skin type, purchasing variants, tracking deliveries, and reviewing products.
- **Administrators (Admin):** Store operations staff managing catalog, variants, stock batches/expiry, orders, payments, promotions, coupons, reviews, customer inquiries, and analytics.
- **Super Administrators (Super Admin):** System owners managing administrator accounts, RBAC roles/permissions, system settings, and security audit logs.

## 5. Definitions and Abbreviations

| Term | Definition |
|---|---|
| **RBAC** | Role-Based Access Control (`customer`, `admin`, `super_admin`) |
| **FEFO** | First Expired, First Out batch stock allocation strategy |
| **COD** | Cash on Delivery payment method |
| **SKU** | Stock Keeping Unit uniquely identifying a product variant |
| **JWT** | JSON Web Token (short-lived access token + rotating/revocable refresh token) |
| **ORM** | Object-Relational Mapping (SQLAlchemy 2.0) |
| **KPI** | Key Performance Indicator |

## 6. Overall System Description

GlowCart follows a three-tier client-server architecture:
1. **Presentation Tier:** React 18 SPA built with TypeScript, Vite, Tailwind CSS, Zustand, TanStack Query, React Hook Form, Zod, and Recharts.
2. **Application Tier:** FastAPI modular monolith (`api/v1` routers → `services` → `repositories` → `models`) with Pydantic v2 validation and middleware.
3. **Data Tier:** PostgreSQL relational database with 27 normalized tables managed by Alembic migrations.

## 7. User Classes and Characteristics

- **Guest / Unauthenticated Visitor:** Can browse public catalog, categories, brands, promotions, search, view product details/reviews, and register/login.
- **Customer (`customer`):** Authenticated shopper with cart, wishlist, saved addresses, checkout, order history/tracking, cancellation requests, verified-purchase reviews, support messages, and notifications.
- **Admin (`admin`):** Authenticated operator with access to `/api/v1/admin/*` endpoints for catalog, variants, inventory, batches, orders, payments, customers, promotions, coupons, reviews, messages, analytics, and reports.
- **Super Admin (`super_admin`):** Full admin capabilities plus admin account creation, role/permission management, audit log inspection, and system settings.

## 8. Operating Environment

- **Frontend Hosting:** Vercel (static SPA + CDN).
- **Backend & Database Hosting:** Railway (FastAPI/Uvicorn container + Railway PostgreSQL).
- **Media Storage:** Cloudinary or compatible object storage adapter (with local static upload fallback in development).
- **Client Browsers:** Modern evergreen desktop, tablet, and mobile browsers (Chrome, Firefox, Safari, Edge) across viewports `375px`, `768px`, `1024px`, and `1440px`.

## 9. Functional Requirements

| ID | Requirement | Actor | Priority |
|---|---|---|---|
| **FR-001** | Register, log in, log out, refresh JWT tokens, manage profile, and reset password. | Customer | High |
| **FR-002** | Manage multiple saved delivery addresses per customer. | Customer | High |
| **FR-003** | Organize cosmetics into 8+ categories and 15+ brands with hierarchical/slug navigation. | Admin / Customer | High |
| **FR-004** | Support 50+ products and 100+ variants with optional cosmetic attributes (shade name/code, color name/HEX, volume ml, weight g, size, skin type). | Admin / Customer | High |
| **FR-005** | Browse, search, paginate, sort (price, newest, rating), and filter (price, brand, category, availability, skin type, shade/color). | Customer | High |
| **FR-006** | Dynamic variant selector displaying selected shade/volume SKU, price, original price, discount, and live stock availability. | Customer | High |
| **FR-007** | Persistent shopping cart with add, update quantity, remove, coupon validation, shipping calculation, and server-side price/stock revalidation at checkout. | Customer | High |
| **FR-008** | Wishlist management (add, remove, view saved items). | Customer | Medium |
| **FR-009** | Promotions and coupon code validation (percentage/fixed discount, usage limits, expiry window, minimum order subtotal). | Admin / Customer | Medium |
| **FR-010** | Transactional checkout supporting Cash on Delivery (COD) and Online Payment Sandbox with idempotency keys and duplicate webhook protection. | Customer / System | High |
| **FR-011** | Preserve immutable order item snapshots (product name, SKU, variant label, unit price) and delivery address snapshot at order placement. | System | High |
| **FR-012** | Enforce 9 valid order statuses (`PENDING`, `PAYMENT_PENDING`, `PAID`, `CONFIRMED`, `PROCESSING`, `SHIPPED`, `DELIVERED`, `CANCELLED`, `REFUNDED`) and legal state transitions. | Admin / System | High |
| **FR-013** | Variant-level inventory (`available_quantity`, `reserved_quantity`, `low_stock_threshold`) and batch-level expiry tracking (`batch_number`, `manufacture_date`, `expiry_date`, `remaining_quantity`). | Admin / System | High |
| **FR-014** | Enforce FEFO allocation on checkout/deduction, block expired batches from sale, prevent negative stock under concurrency, and log all movements (`RECEIVED`, `SOLD`, `ADJUSTED`, `RETURNED`, `RESERVED`, `RELEASED`). | System / Admin | High |
| **FR-015** | Customer reviews with ratings (1–5), verified-purchase indicator, duplicate review prevention per product/user, edit/delete own review, and admin moderation. | Customer / Admin | Medium |
| **FR-016** | Customer support messages, admin replies, and user notifications. | Customer / Admin | Medium |
| **FR-017** | Admin analytics calculated from real DB records: KPI cards, daily/weekly/monthly/yearly revenue, sales by category/brand, best-sellers, lipstick/foundation shade analytics, volume/color breakdown, and inventory status. | Admin | High |
| **FR-018** | Super Admin management of admin users, roles/permissions, system settings, and immutable audit logs. | Super Admin | High |

## 10. Non-Functional Requirements

| ID | Category | Requirement |
|---|---|---|
| **NFR-001** | Security | Hash passwords with Argon2id (or bcrypt only when Argon2id binary is unavailable); sign JWTs with HS256/secret env var; enforce RBAC server-side on every protected endpoint. |
| **NFR-002** | Security | Zero raw card/CVV storage; server-side payment verification; parameterized ORM queries only; rate limiting on auth/payment endpoints; CORS allowlist. |
| **NFR-003** | Reliability | Concurrency-safe stock reservation/deduction via database transactions and row locking (`SELECT ... FOR UPDATE` where supported); idempotent order & webhook handling. |
| **NFR-004** | Performance | Indexed foreign keys and search/filter columns; pagination on list endpoints; target normal API p95 < 200 ms and page load < 3 s (measured under documented test conditions, not guaranteed). |
| **NFR-005** | Accessibility & UX | WCAG AA contrast (4.5:1 body / 3:1 large), visible `--color-ring` focus indicators, minimum `44×44px` touch targets, `8px` spacing, zero horizontal overflow across `375px`–`1440px`. |
| **NFR-006** | Maintainability | Modular layered architecture (`api → services → repositories → models`), TypeScript strictness, Alembic forward migrations, and synchronized documentation. |

## 11. External Interface Requirements

- **User Interface:** Responsive React SPA with Customer Storefront and Admin Sidebar Dashboard.
- **API Interface:** JSON REST API under `/api/v1` with OpenAPI/Swagger documentation at `/docs` and ReDoc at `/redoc`.
- **Payment Interface:** Pluggable payment provider abstraction with `CODAdapter` and `SandboxPaymentAdapter` (supporting webhook signature/idempotency verification).
- **Storage Interface:** Pluggable image storage service supporting Cloudinary credentials or local filesystem fallback.

## 12. Software and Hardware Requirements

- **Development / Server:** Python 3.12+, PostgreSQL 15+, Node.js 20+ (for frontend build/Vitest).
- **Client:** Any modern web browser with JavaScript enabled, 1 GB+ RAM, viewport ≥ 375px width.

## 13. System Constraints

- Base currency fixed to USD (`NUMERIC(12, 2)`).
- No raw SQL string concatenation; all schema evolution via Alembic.
- Secrets must reside in `.env` (never committed to VCS).

## 14. Assumptions and Dependencies

- External credentials (Cloudinary, live payment gateways, SMTP) may be absent in local/academic environments; pluggable sandbox/mock adapters satisfy those interfaces cleanly.
- If Node.js/PostgreSQL daemon is unavailable in a restricted test sandbox, backend verification runs against SQLite-compatible SQLAlchemy tests while preserving PostgreSQL production compatibility.

## 15. Acceptance Criteria

Mapped to Section 20 of `implementation_plan.md`: all 32 acceptance checklist items must be implemented and backed by verified code, tests, or documented environment blockers before final closure.

