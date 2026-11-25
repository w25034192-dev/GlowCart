# Changelog — GlowCart

All notable changes to the GlowCart project are documented in this file.

## [1.0.1] - 2026-11-25
### Changed
- Generated and persisted `design-system/glowcart/` (`MASTER.md`, `tokens.json`, `tokens.css`, `pages/admin-dashboard.md`) via `ui-ux-pro-max-skill`.
- Upgraded frontend typography (`Cormorant` + `Montserrat` + `Fira Code`), semantic tokens, focus-not-obscured `scroll-padding-top`, skip-to-content link, `useDeferredValue` search/filter debouncing, and button/card contrast and spacing.

## [1.0.0] - 2026-11-25
### Added
- **Backend (`backend/`):** 27-table SQLAlchemy 2.0 schema, initial Alembic migration, FastAPI `/api/v1` routers for auth/RBAC, addresses, catalog, variants, FEFO batch inventory, cart, wishlist, promotions/coupons, transactional orders with snapshots, COD & HMAC-signed sandbox payments, verified-purchase reviews, support messages, notifications, SQL analytics, CSV exports, and demo catalog seeder (`8` categories, `20` brands, `50` products, `120+` variants).
- **Frontend (`frontend/`):** Complete React 18 + TypeScript + Vite + Tailwind CSS storefront and 18-module Admin Dashboard with semantic beauty tokens, Recharts analytics, Zustand stores, TanStack Query hooks, and Vitest test specs.
- **Documentation (`docs/`, `README.md`):** SRS, System Architecture, Database Design, API Specification, 5 Mermaid Diagrams, User Stories, Use Cases, Installation/Deployment/User Manuals, Testing Strategy & Report, and 7-Chapter Final Academic Project Report with Abstract, Presentation Outline, and Viva Q&A.
- **Verification & Hardening:** Remediated finalized-order cancellation FEFO restocking, added fail-closed production secret validation, and migrated Recharts colors to semantic CSS variables.

## [0.1.0] - 2026-11-25
### Added
- Integrated Universal Markdown Skills Framework (UMSF) via `.agents/skills.json` and root `AGENTS.md`.
- Phase 1 planning and architecture documentation suite.
