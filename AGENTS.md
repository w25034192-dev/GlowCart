# AGENTS.md — GlowCart Operating Protocol (UMSF)

This repository adopts the **Universal Markdown Skills Framework (UMSF)** located in `./Universal-Markdown-Skills-Framework/` alongside the project specification in `./implementation_plan.md`.

## Canonical Framework References

- **Entry Point & Tripartite Roles**: [UMSF AGENTS.md](./Universal-Markdown-Skills-Framework/AGENTS.md)
- **Mandatory Constraints & Invariants**: [UMSF RULES.md](./Universal-Markdown-Skills-Framework/RULES.md)
- **12-Stage Development Lifecycle**: [UMSF WORKFLOW.md](./Universal-Markdown-Skills-Framework/WORKFLOW.md)
- **Central Skill Registry (77 Skills / 16 Domains)**: [UMSF SKILLS.md](./Universal-Markdown-Skills-Framework/SKILLS.md)
- **Project Architecture & Requirements**: [implementation_plan.md](./implementation_plan.md)

All 77 UMSF skills are registered for Antigravity workspace discovery via [`.agents/skills.json`](./.agents/skills.json).

## Core Operating Rules for GlowCart

1. **Precedence Hierarchy**:
   - Tier A (Absolute): Platform safety, credential protection, non-destructive boundaries.
   - Tier B (UMSF Rules): Mandatory invariants in `./Universal-Markdown-Skills-Framework/RULES.md`.
   - Tier C (Project Spec): Explicit user prompts and `./implementation_plan.md` (React + TypeScript + Vite + Tailwind CSS, Python FastAPI, PostgreSQL + SQLAlchemy 2.0 + Alembic, JWT + Argon2id, Customer / Admin / Super Admin RBAC).
2. **Progressive Skill Loading**:
   - Consult `SKILLS.md` and load only task-relevant skills.
   - Read Level 1 MVP Summary (lines 1–55 of `SKILL.md`) first; load Level 2 core instructions and Level 3 `references/` only when needed.
3. **Mandatory TDD (Red-Green-Refactor)**:
   - Write failing tests first (RED), confirm expected failure, implement minimal passing code (GREEN), and clean up while keeping tests green (REFACTOR). Never claim completion without executed test output and exit code `0`.
4. **Tripartite Agent Verification**:
   - **Agent A (Primary Dev)** implements via TDD and never self-approves completion.
   - **Agent B (Independent Verification Subagent)** audits requirements, diffs, architecture, code quality, tests, security coordination, and docs (`independent-verification-subagent`), bounded to `MAX_VERIFICATION_ITERATIONS = 3`.
   - **Agent C (Independent Security)** reviews high-risk changes: auth, JWT/Argon2id, RBAC, payments, public APIs, and schema changes (`independent-security-review-agent`).
   - Prefer isolated subagents via `invoke_subagent`; if running single-agent sequential passes, state so explicitly.
5. **Risk-Proportionate 12-Stage Lifecycle & Release Gates**:
   - Scale rigor by risk tier (Low / Medium / High) across Functional, Regression, Security, and Documentation gates.
   - Use `feature-integration-verification` and `post-task-verification` before closing multi-tier features.
6. **Frontend & UI/UX Pro Max Standards**:
   - Enforce WCAG AA contrast (4.5:1 body / 3:1 large text), visible `--color-ring` focus indicators, minimum `44x44px` touch targets with `8px` spacing, semantic CSS tokens (no raw hex values in components), mobile-first responsive layouts (`375px`, `768px`, `1024px`, `1440px`) with zero horizontal overflow, GPU-only animations (`transform`/`opacity`, `150–250ms`, `prefers-reduced-motion`), and accessible SVGs (never raw emojis as UI icons).
7. **Security, Database & Documentation Hygiene**:
   - Zero hardcoded secrets; parameterized ORM queries only; server-side RBAC on every protected endpoint; forward-safe Alembic migrations (`database-migrations`); avoid N+1 queries (`database-query-optimization`).
   - Keep `DEVELOPMENT_STATUS.md` and project docs synchronized using portable relative links; store UMSF audit/test/security logs in `./docs_agent/` only when real verified output exists.

