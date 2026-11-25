# Design and Development of an International Web-Based Cosmetic E-Commerce and Inventory Management System with Sales Analytics (GlowCart)

---

## Preliminary Pages

### Title Page
- **Project Title:** Design and Development of an International Web-Based Cosmetic E-Commerce and Inventory Management System with Sales Analytics (GlowCart)
- **Student Name:** `[STUDENT NAME PLACEHOLDER]`
- **Student ID:** `[STUDENT ID PLACEHOLDER]`
- **Department / Faculty:** `[DEPARTMENT / FACULTY PLACEHOLDER]`
- **Institution:** `[UNIVERSITY / INSTITUTION PLACEHOLDER]`
- **Supervisor:** `[SUPERVISOR NAME PLACEHOLDER]`
- **Submission Date:** `[SUBMISSION DATE PLACEHOLDER]`

### Declaration
> I hereby declare that the project work presented in this report is an original academic software engineering project developed under the supervision of `[SUPERVISOR NAME PLACEHOLDER]`, and has not been submitted elsewhere for any degree.  
> Signature: `____________________` · Date: `[DATE PLACEHOLDER]`

### Acknowledgement
`[ACKNOWLEDGEMENT PLACEHOLDER — Express gratitude to academic supervisor, faculty reviewers, peers, and family.]`

### Abstract
See [docs/abstract.md](./abstract.md).

### Table of Contents
1. Chapter 1 — Introduction
2. Chapter 2 — Literature Review
3. Chapter 3 — Requirements Analysis
4. Chapter 4 — System Design
5. Chapter 5 — System Implementation
6. Chapter 6 — Testing and Results
7. Chapter 7 — Conclusion and Future Work
8. References and Appendices

### List of Figures
- Figure 1: Three-Tier System Architecture ([`docs/diagrams/system-architecture.mmd`](./diagrams/system-architecture.mmd))
- Figure 2: 27-Table Entity Relationship Diagram ([`docs/diagrams/er-diagram.mmd`](./diagrams/er-diagram.mmd))
- Figure 3: Actor Use Case Diagram ([`docs/diagrams/use-case-diagram.mmd`](./diagrams/use-case-diagram.mmd))
- Figure 4: Checkout & FEFO Allocation Activity Diagram ([`docs/diagrams/activity-diagram.mmd`](./diagrams/activity-diagram.mmd))
- Figure 5: Payment & Webhook Verification Sequence Diagram ([`docs/diagrams/sequence-diagram.mmd`](./diagrams/sequence-diagram.mmd))

### List of Tables
- Table 1: Functional & Non-Functional Requirements Summary (`docs/SRS.md`)
- Table 2: 27 Core Relational Database Tables (`docs/database-design.md`)
- Table 3: Executed Backend Test Verification Matrix (`docs/testing-report.md`)

### Abbreviations
- **API:** Application Programming Interface
- **COD:** Cash on Delivery
- **ERD:** Entity Relationship Diagram
- **FEFO:** First Expired, First Out
- **JWT:** JSON Web Token
- **ORM:** Object-Relational Mapping
- **RBAC:** Role-Based Access Control
- **SKU:** Stock Keeping Unit
- **SRS:** Software Requirements Specification

---

## Chapter 1 — Introduction

### 1.1 Background
Cosmetic e-commerce differs significantly from generic retail because products depend heavily on shade variants (color names, HEX swatches), volume/size variations (e.g., 30 ml vs. 50 ml serums), skin-type suitability, and strict shelf-life expiry constraints.

### 1.2 Problem Statement
Generic online stores often lack variant-level SKU stock separation, batch expiry tracking, and FEFO allocation, creating risks of overselling, dispatching expired cosmetics, and misreporting revenue when orders are cancelled or refunded.

### 1.3 Project Aim & Objectives
To design, implement, test, and document **GlowCart**, a full-stack international cosmetic e-commerce platform (USD base currency) integrating shade/volume catalog management, batch expiry FEFO inventory control, transactional payment processing, and real-time sales analytics.

### 1.4 Scope, Significance & Limitations
GlowCart covers Customer, Admin, and Super Admin workflows across 27 PostgreSQL tables, FastAPI `/api/v1` endpoints, and a React + TypeScript + Tailwind CSS web interface. Limitations include sandbox payment verification (non-production gateway), local image storage fallback when Cloudinary credentials are absent, and unexecuted frontend Vitest/Vite build in the offline authoring environment lacking Node.js.

---

## Chapter 2 — Literature Review

### 2.1 Overview & Domain Analysis
Modern e-commerce architectures leverage RESTful APIs, relational ACID databases for inventory integrity, and component-based single-page applications. Cosmetic platforms additionally require rich variant modeling and batch traceability similar to pharmaceutical/perishable supply chains using FEFO (First Expired, First Out).

### 2.2 Technology Evaluation & Research Gap
Combining React + TypeScript + Vite (client state via Zustand, server caching via TanStack Query, charts via Recharts) with Python FastAPI + SQLAlchemy 2.0 + Alembic + PostgreSQL bridges rapid typed API development with strict database constraints.

> **Verification Note:** Formal academic citations (textbooks, peer-reviewed papers on e-commerce inventory and FEFO optimization) have not been fetched from external bibliographic databases in this offline workspace and are marked `[FOR FURTHER ACADEMIC CITATION VERIFICATION]` prior to final university submission.

---

## Chapter 3 — Requirements Analysis
Full stakeholder analysis, 18 functional requirements (`FR-001`–`FR-018`), 6 non-functional requirements (`NFR-001`–`NFR-006`), user stories, and use cases are documented in [docs/SRS.md](./SRS.md), [docs/user-stories.md](./user-stories.md), and [docs/use-cases.md](./use-cases.md).

---

## Chapter 4 — System Design
- **Architecture:** Modular three-tier FastAPI + React + PostgreSQL design ([docs/architecture.md](./architecture.md)).
- **Database Design:** 27 normalized tables with UUID PKs, `NUMERIC(12,2)` money fields, check constraints, and order item/address snapshots ([docs/database-design.md](./database-design.md)).
- **Security Design:** JWT access/refresh tokens with revocation, Argon2id (with bcrypt fallback where native binary is absent), server-side RBAC, HMAC-SHA256 webhook verification, sliding-window rate limiting, and `audit_logs`.

---

## Chapter 5 — System Implementation
- **Backend (`backend/`):** Implemented in Python 3.12 + FastAPI (`app/api/v1/*`, `app/services/*`, `app/models/*`), Alembic migration `9d984bd1e8dc_initial_schema.py`, and `app/db/seed.py` seeding 8 categories, 20 brands, 50 products, and 120+ variants.
- **Frontend (`frontend/`):** Implemented in React 18 + TypeScript + Vite + Tailwind CSS (`CustomerLayout`, `AdminLayout`, dynamic shade/volume selector, cart/checkout, Recharts dashboard, and 18 admin sidebar sections).

---

## Chapter 6 — Testing and Results
All 15 backend integration and concurrency tests executed via `pytest tests -v` passed (exit code `0`), empirically confirming RBAC isolation (`403`), expired batch rejection (`409`), last-unit concurrency safety (`[201, 409]`), duplicate webhook idempotency, historical order price snapshot immutability, and analytics exclusion of cancelled/refunded orders. Frontend Vitest specs are authored in `frontend/src/test/App.test.tsx` and pending Node.js execution. Performance latency targets (`< 200 ms` p95) were not benchmarked under load in this environment and remain targets rather than measured results. See [docs/testing-report.md](./testing-report.md).

---

## Chapter 7 — Conclusion and Future Work
GlowCart achieves its core architectural, functional, security, and documentation objectives. Future enhancements include live Stripe/PayPal webhook integration, multi-currency conversion, automated CI/CD GitHub Actions pipelines, and email/SMS notification delivery.

---

## References and Appendices
- **Appendix A:** Installation Guide — [docs/installation-guide.md](./installation-guide.md)
- **Appendix B:** Deployment Guide — [docs/deployment-guide.md](./deployment-guide.md)
- **Appendix C:** API Specification — [docs/api-specification.md](./api-specification.md)
- **Appendix D:** User Manual — [docs/user-manual.md](./user-manual.md)
- **Appendix E:** References — `[TO BE POPULATED WITH VERIFIED BIBLIOGRAPHIC CITATIONS]`

