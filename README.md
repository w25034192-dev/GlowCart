# GlowCart — International Cosmetic E-Commerce & Inventory Management System with Sales Analytics

## 1. Project Name
**GlowCart** (Academic Title: *Design and Development of an International Web-Based Cosmetic E-Commerce and Inventory Management System with Sales Analytics*).

## 2. Project Overview
GlowCart is a full-stack cosmetic e-commerce platform combining a shade/volume-aware customer storefront with batch-level FEFO (First Expired, First Out) inventory tracking, transactional checkout/payment verification, and real-time SQL-backed sales analytics.

## 3. Project Objectives
- Deliver an international USD-based cosmetic storefront organized by categories and brands.
- Support cosmetic-specific product variants (shade name/code, HEX swatch, volume ml, weight g, size).
- Enforce batch expiry validation and FEFO stock allocation preventing negative inventory or expired sales.
- Provide JWT + Argon2id (with bcrypt fallback when Argon2id binary is absent) authentication and server-side RBAC (`customer`, `admin`, `super_admin`).
- Deliver a Recharts admin analytics dashboard powered by real database records.

## 4. Main Features
- **Customer Storefront:** Catalog browsing, multi-facet filtering (category, brand, price, skin type, shade/color, stock), dynamic shade/volume variant selector, cart, wishlist, coupons, checkout (COD & Online Sandbox), order tracking, verified-purchase reviews, support messages, notifications.
- **Admin Dashboard:** 18-section sidebar covering products, categories, brands, variants, inventory, batches/expiry alerts, orders, payments/refunds, customers, promotions, coupons, review moderation, support replies, Recharts analytics, CSV reports, settings, and Super Admin audit logs.

## 5. Technology Stack
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, React Router, Axios, TanStack Query, Zustand, React Hook Form, Zod, Recharts, Lucide React.
- **Backend:** Python 3.12+, FastAPI, SQLAlchemy 2.0, Pydantic v2, Alembic, PostgreSQL, PyJWT, Argon2id (`argon2-cffi`) / bcrypt.
- **Testing:** Pytest + HTTPX (backend), Vitest + React Testing Library (frontend).

## 6. Architecture Overview
Three-tier modular monolith (`frontend/` SPA → `backend/app/api/v1` → `services` → `repositories` → `models` → `PostgreSQL`), documented in [docs/architecture.md](./docs/architecture.md).

## 7. Project Folder Structure
```text
GlowCart/
├── backend/
│   ├── alembic/             # Alembic migrations (27 tables)
│   ├── app/
│   │   ├── api/v1/          # Versioned REST routers
│   │   ├── core/            # Config, JWT/Argon2id security, rate limiter
│   │   ├── db/              # Engine, session, demo seeder
│   │   ├── models/          # 27 SQLAlchemy 2.0 ORM tables
│   │   ├── repositories/    # Data access helpers
│   │   ├── schemas/         # Pydantic v2 contracts
│   │   └── services/        # Business logic (FEFO, orders, payments, analytics)
│   ├── tests/               # Pytest integration & concurrency suite
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # Reusable UI & ProductCard
│   │   ├── layouts/         # CustomerLayout & AdminLayout
│   │   ├── pages/           # customer/ and admin/ views
│   │   ├── routes/          # ProtectedRoute RBAC guards
│   │   ├── services/        # Axios API client & interceptors
│   │   ├── store/           # Zustand authStore & cartStore
│   │   ├── test/            # Vitest + RTL specs
│   │   └── types/           # TypeScript contracts
│   └── package.json
├── docs/                    # SRS, Architecture, DB Design, API Spec, Manuals, Report
├── docker-compose.yml
├── DEVELOPMENT_STATUS.md
└── CHANGELOG.md
```

## 8. Prerequisites
- Python 3.12+
- PostgreSQL 15+ (or SQLite for local test mode)
- Node.js 20+ & npm (for frontend build/Vitest)
- Optional: Docker & Docker Compose

## 9. Installation Instructions
See [docs/installation-guide.md](./docs/installation-guide.md) for full macOS and Windows steps.

## 10. Environment Variable Setup
Copy `.env.example` to `.env` in root, `backend/.env.example` to `backend/.env`, and `frontend/.env.example` to `frontend/.env`.

## 11. Database Setup & 12. Alembic Migrations
```bash
cd backend
alembic upgrade head
python3 -m app.db.seed
```

## 13. Backend Startup Instructions
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

## 14. Frontend Startup Instructions
```bash
cd frontend
npm install
npm run dev
```

## 15. Test Instructions
```bash
cd backend && python3 -m pytest tests -v
cd frontend && npm test
```

## 16. Demo Account Setup
Running `python3 -m app.db.seed` creates clearly labelled illustrative demo accounts:
- Customer: `customer@glowcart.com` / `GlowCartDemo123!`
- Admin: `admin@glowcart.com` / `GlowCartAdmin123!`
- Super Admin: `superadmin@glowcart.com` / `GlowCartSuper123!`

## 17. API Documentation URL
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/api/v1/openapi.json`

## 18. Deployment Overview
GlowCart includes multi-stage Dockerfiles and `railway.toml` configurations in both [`backend/`](./backend/) and [`frontend/`](./frontend/) for full-stack Railway deployment (plus [`docker-compose.yml`](./docker-compose.yml) / [`docker-compose.prod.yml`](./docker-compose.prod.yml) for local Docker development and [`frontend/vercel.json`](./frontend/vercel.json) for optional Vercel frontend hosting). See [docs/deployment-guide.md](./docs/deployment-guide.md).

## 19. Troubleshooting
- **Database connection refused:** Verify PostgreSQL is running and `DATABASE_URL` matches credentials.
- **CORS blocked:** Add frontend origin to `CORS_ORIGINS` in `backend/.env`.

## 20. Project Limitations
- Online payments use a local HMAC-signed sandbox adapter rather than live Stripe/card settlement.
- Image uploads default to local `/uploads/products` unless Cloudinary credentials are supplied.
- Frontend `npm test` / `vite build` require Node.js 20+ (not pre-installed in the offline authoring sandbox).

