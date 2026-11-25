# MASTER AGENTIC CODING PROMPT — GLOWCART

## 1. PROJECT IDENTITY

**Project Name:** GlowCart

**Academic Project Title:**

Design and Development of an International Web-Based Cosmetic E-Commerce and Inventory Management System with Sales Analytics.

**Project Type:** University Final-Year Software Engineering Project

**Project Level:** Advanced Full-Stack Web Application

**Target Market:** International

**Base Currency:** USD

**Frontend:** React + TypeScript + Vite + Tailwind CSS

**Backend:** Python FastAPI

**Database:** PostgreSQL

**ORM:** SQLAlchemy 2.0

**Database Migration:** Alembic

**Authentication:** JWT + Argon2id password hashing

**Deployment:** Vercel (Frontend), Railway (Backend and PostgreSQL)

**Product Image Storage:** Cloudinary or compatible object storage

---

# 2. YOUR ROLE AS AN AUTONOMOUS DEVELOPMENT AGENT

Act as a senior full-stack software engineer, software architect, UI/UX designer, database engineer, QA engineer, DevOps engineer, technical writer, and academic project documentation specialist.

Your responsibility is to design, develop, test, document, and prepare the complete GlowCart application.

Do not build only a frontend prototype.

Do not build only a backend API.

Do not stop after creating the project structure or database.

Build a functional, integrated, production-oriented application suitable for a university final-year project demonstration.

## Mandatory development rules

1. First inspect the existing repository and understand its current structure.
2. Never overwrite existing working code without inspecting it.
3. Create a development plan before implementation.
4. Implement the project in manageable phases.
5. Connect the frontend, backend, and database properly.
6. Use reusable components and modular architecture.
7. Use real database operations instead of hardcoded production data.
8. Run tests after implementing each major feature.
9. Fix errors before moving to the next phase.
10. Update documentation whenever architecture, APIs, database models, or features change.
11. Maintain a `DEVELOPMENT_STATUS.md` file.
12. Do not claim a feature is complete unless it has been implemented and verified.
13. Do not fabricate test results, screenshots, academic references, or performance measurements.
14. If credentials or external services are unavailable, implement the integration interface and continue with other independent tasks.
15. Do not stop after planning. Continue implementing all phases until the acceptance criteria are satisfied.

---

# 3. PROJECT OVERVIEW

GlowCart is an international cosmetic e-commerce platform with integrated inventory management and sales analytics.

The platform allows customers to discover cosmetic products, select product variants, purchase products, track orders, and submit reviews.

Administrators can manage products, categories, brands, inventory, expiry dates, customers, orders, payments, promotions, and sales reports.

The system must provide three roles:

- Customer
- Admin
- Super Admin

## Main objectives

- Develop an international online cosmetic shopping platform.
- Provide organized cosmetic product categories and brands.
- Support product variants such as shades, colors, sizes, and volumes.
- Manage stock quantities and expiry dates.
- Support customer registration, authentication, and authorization.
- Provide a complete shopping cart and checkout process.
- Manage orders and payment records.
- Generate sales and inventory analytics.
- Provide a secure and responsive user interface.
- Produce complete technical and academic documentation.

---

# 4. TECHNOLOGY STACK

## Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- React Router
- Axios
- TanStack Query
- Zustand
- React Hook Form
- Zod
- Recharts
- Lucide React

## Backend

- Python
- FastAPI
- SQLAlchemy 2.0
- Pydantic
- Alembic
- PostgreSQL
- JWT authentication
- Argon2id password hashing
- Pytest

## Testing

- Pytest
- Vitest
- React Testing Library
- API integration testing
- Security testing
- Performance testing

## Deployment

- Vercel
- Railway
- Railway PostgreSQL
- Cloudinary or object storage
- Docker

Use compatible, maintained library versions. Pin dependencies and document the supported runtime versions.

---

# 5. COSMETIC PRODUCT CATALOG

Create a realistic cosmetic shopping catalog.

## Categories

1. Makeup
   - Foundation
   - Concealer
   - Lipstick
   - Lip Gloss
   - Lip Tint
   - Blush
   - Mascara
   - Eyeliner
   - Eyeshadow
   - Setting Powder

2. Skincare
   - Cleanser
   - Toner
   - Serum
   - Essence
   - Moisturizer
   - Face Mask

3. Sun Care
   - Sunscreen
   - Sun Stick

4. Hair Care
   - Shampoo
   - Conditioner
   - Hair Mask
   - Hair Serum

5. Body Care
   - Body Lotion
   - Body Wash
   - Body Scrub

6. Fragrance
   - Perfume
   - Body Mist

7. Beauty Tools
   - Makeup Brushes
   - Beauty Sponges
   - Mirrors

8. Makeup Sets
   - Makeup Kits
   - Gift Sets
   - Skincare Bundles

## Suggested brands

Maybelline, L'Oréal Paris, MAC, NYX, Rare Beauty, Fenty Beauty, Huda Beauty, e.l.f. Cosmetics, Charlotte Tilbury, The Ordinary, CeraVe, COSRX, Beauty of Joseon, Anua, La Roche-Posay, Cetaphil, Neutrogena, SKIN1004, Round Lab, Torriden, Dior, NARS, Olaplex, TRESemmé, Sol de Janeiro.

## Sample products

- Maybelline Fit Me Foundation
- Maybelline SuperStay Matte Ink
- NYX Butter Gloss
- Fenty Beauty Gloss Bomb
- Rare Beauty Soft Pinch Blush
- NARS Radiant Creamy Concealer
- Huda Beauty Easy Bake Powder
- The Ordinary Niacinamide 10% + Zinc 1%
- COSRX Advanced Snail 96 Mucin Essence
- Beauty of Joseon Relief Sun
- CeraVe Moisturizing Cream
- Anua Heartleaf 77% Toner
- SKIN1004 Centella Ampoule
- Round Lab 1025 Dokdo Toner
- Torriden Dive-In Serum
- Biodance Bio-Collagen Mask
- K18 Leave-In Hair Mask
- Olaplex Hair Treatment
- YSL Libre
- Miss Dior Blooming Bouquet
- Sol de Janeiro Cheirosa 62
- Victoria's Secret Bare Vanilla

Seed at least:
- 8 product categories
- 15 brands
- 50 products
- 100 product variants

Use clearly identified demo data. Sample prices must be marked illustrative. Do not invent product ingredients, certifications, manufacturer claims, popularity statistics, or expiry dates. Use verified product information where available.

---

# 6. PRODUCT VARIANTS

This is an important cosmetic-specific feature.

A product may have multiple variants.

Examples:

Foundation:
- Porcelain
- Ivory
- Natural Beige
- Warm Beige
- Honey

Lipstick:
- Red
- Pink
- Nude
- Brown

Skincare:
- 15 ml
- 30 ml
- 50 ml
- 100 ml

Each variant should support:

- Variant ID
- Product ID
- SKU
- Shade name
- Shade code
- Color name
- HEX color value
- Volume in ml
- Weight in grams
- Size
- Price
- Original price
- Availability
- Status

Do not force every attribute onto every product. Use optional, product-appropriate attributes.

Create a dynamic variant selector on the product details page.

For example, when a customer selects a foundation shade, display the selected shade and its corresponding SKU, price, and availability.

---

# 7. CUSTOMER FEATURES

Implement all the following features.

## Authentication

- Register
- Login
- Logout
- Refresh token
- Forgot password
- Reset password
- Profile management
- Address management

Use secure password hashing and JWT authentication.

## Homepage

Include:

- Navigation bar
- GlowCart logo
- Search bar
- Category navigation
- Hero banner
- New arrivals
- Best sellers
- Featured brands
- Product collections
- Special offers
- Customer reviews
- Newsletter section
- Footer

## Product browsing

Customers can:

- Browse all products.
- Browse by category.
- Browse by brand.
- Search by product name.
- Filter by price.
- Filter by brand.
- Filter by category.
- Filter by availability.
- Filter by skin type when applicable.
- Filter by shade or color when applicable.
- Sort by price.
- Sort by newest.
- Sort by rating.
- Use pagination.

## Product details

Display:

- Product images
- Product name
- Brand
- Category
- Description
- Price
- Original price
- Discount
- Variant selector
- Shade selector
- Volume selector
- Availability
- Product specifications
- Ingredients only when verified
- Customer reviews
- Related products

## Shopping cart

- Add to cart
- Remove from cart
- Update quantity
- Calculate subtotal
- Apply coupon
- Calculate discount
- Calculate shipping
- Calculate final total

Revalidate price and stock on the server during checkout.

## Wishlist

- Add products
- Remove products
- View saved products

## Checkout

- Select delivery address.
- Add a new address.
- Select payment method.
- Apply coupon.
- Review order.
- Confirm purchase.

## Payment methods

Implement:

1. Cash on Delivery
2. Online payment sandbox integration

Never store raw card numbers or CVV.

Never trust frontend payment success. Verify payment status using the provider's server-side verification or webhook mechanism.

If payment credentials are unavailable, build a clearly labelled sandbox/mock adapter for development and document how to configure a real provider.

## Order management

Customers can:

- View order history.
- View order details.
- Track order status.
- View payment status.
- Request cancellation where allowed.

## Reviews

- Submit reviews.
- Add ratings.
- Edit own reviews.
- Delete own reviews.
- Display verified-purchase status.
- Prevent duplicate reviews where appropriate.

## Customer service

- Submit customer messages.
- View message history.
- Receive admin replies.
- View notifications.

---

# 8. ADMIN DASHBOARD

Create a professional admin interface with sidebar navigation.

## Sidebar

- Dashboard
- Products
- Categories
- Brands
- Variants
- Inventory
- Batches & Expiry
- Orders
- Payments
- Customers
- Promotions
- Coupons
- Reviews
- Messages
- Notifications
- Analytics
- Reports
- Settings

## Dashboard KPI cards

Display:

- Total revenue
- Total orders
- Total customers
- Total products
- Pending orders
- Low-stock products
- Out-of-stock products
- Near-expiry batches

## Analytics charts

Use Recharts.

Create:

- Daily revenue chart
- Weekly revenue chart
- Monthly revenue chart
- Yearly revenue chart
- Sales by category
- Sales by brand
- Best-selling products
- Best-selling lipstick shades
- Best-selling foundation shades
- Variant sales by color
- Variant sales by volume
- Inventory status chart

All production analytics must be calculated from real database records.

Do not use hardcoded numbers for actual business KPI results. Demo seed data may be used for demonstration, but identify it as demo data.

## Admin management

Admins can:

- Create products.
- Update products.
- Delete or archive products.
- Manage categories.
- Manage brands.
- Manage variants.
- Upload product images.
- Manage stock.
- Manage inventory batches.
- Review orders.
- Update order status.
- Review payments.
- Manage customers.
- Create promotions.
- Create coupons.
- Moderate reviews.
- Reply to customer messages.
- View analytics.
- Export reports.

## Super Admin

Super Admin can:

- Create admin accounts.
- Manage roles.
- Assign permissions.
- View audit logs.
- Manage system settings.

Implement role-based access control on the backend, not only by hiding frontend navigation.

---

# 9. INVENTORY MANAGEMENT

Implement proper inventory management.

## Inventory

Each product variant should have its own stock record.

Include:

- Variant ID
- Available quantity
- Reserved quantity
- Low-stock threshold
- Updated date

## Batch management

Cosmetic products require expiry tracking.

Each inventory batch should contain:

- Batch ID
- Variant ID
- Batch number
- Manufacture date
- Expiry date
- Initial quantity
- Remaining quantity
- Received date

## Inventory alerts

Display:

- Low stock
- Out of stock
- Expiring soon
- Expired batches

Expired batches must never be sold.

Use an appropriate stock allocation strategy, such as FEFO (First Expired, First Out), where applicable.

## Stock movement history

Record:

- Stock received
- Stock sold
- Stock adjusted
- Stock returned
- Stock reserved
- Stock released

Every stock adjustment must have an audit record and an explanation.

Prevent negative inventory and overselling through transactional database operations and concurrency-safe stock updates.

---

# 10. ORDER AND PAYMENT LOGIC

Use these order statuses:

- PENDING
- PAYMENT_PENDING
- PAID
- CONFIRMED
- PROCESSING
- SHIPPED
- DELIVERED
- CANCELLED
- REFUNDED

Define and enforce valid status transitions.

COD orders should remain unpaid until payment is collected.

Online payments must be verified server-side.

Implement:

- Transaction-safe order creation
- Stock reservation
- Stock deduction
- Stock release on eligible cancellation
- Payment transaction records
- Idempotency for repeated requests
- Duplicate webhook protection
- Order item snapshots
- Historical delivery address snapshots

A product's name, SKU, selected variant, and unit price at purchase must be preserved in the order item even if the catalog changes later.

Do not allow customers to directly change protected order statuses.

Revenue reports must handle cancelled and refunded orders correctly.

---

# 11. DATABASE DESIGN

Use PostgreSQL and SQLAlchemy 2.0.

Create these 27 core tables:

1. users
2. roles
3. addresses
4. categories
5. brands
6. products
7. product_images
8. product_variants
9. inventory
10. inventory_batches
11. inventory_movements
12. carts
13. cart_items
14. wishlists
15. wishlist_items
16. orders
17. order_items
18. payments
19. payment_transactions
20. promotions
21. coupons
22. coupon_usages
23. reviews
24. customer_messages
25. message_replies
26. notifications
27. audit_logs

Use UUID primary keys where appropriate.

Include:

- Foreign keys
- Unique constraints
- Check constraints
- Indexes
- Created timestamps
- Updated timestamps
- Appropriate deletion behavior
- NUMERIC/DECIMAL for monetary values

Use separate relational records for variants, inventory, and stock movements. Do not store variant lists as comma-separated strings.

An order must preserve its own address and item snapshots.

Create a clear ERD showing all relationships and cardinalities.

Use Alembic migrations for schema changes. Do not rely on automatic table creation as the production migration strategy.

---

# 12. BACKEND API DESIGN

Use the base path:

`/api/v1`

Create organized routers and schemas.

## Authentication

- POST /auth/register
- POST /auth/login
- POST /auth/refresh
- POST /auth/logout
- GET /auth/me
- POST /auth/forgot-password

## Products

- GET /products
- GET /products/{id}
- GET /products/search
- POST /admin/products
- PUT /admin/products/{id}
- DELETE /admin/products/{id}

## Categories and brands

- GET /categories
- POST /admin/categories
- PUT /admin/categories/{id}
- GET /brands
- POST /admin/brands

## Variants

- GET /products/{id}/variants
- POST /admin/variants

## Cart

- GET /cart
- POST /cart/items
- PUT /cart/items/{id}
- DELETE /cart/items/{id}

## Wishlist

- GET /wishlist
- POST /wishlist/items
- DELETE /wishlist/items/{id}

## Orders

- POST /orders
- GET /orders
- GET /orders/{id}
- GET /admin/orders
- PATCH /admin/orders/{id}/status

## Payments

- POST /payments
- GET /payments/{id}
- POST /payments/webhook
- POST /admin/payments/{id}/refund

## Inventory

- GET /admin/inventory
- POST /admin/inventory/adjustments
- GET /admin/inventory/low-stock
- GET /admin/inventory/expiring

## Reviews

- POST /reviews
- GET /products/{id}/reviews
- PUT /reviews/{id}
- DELETE /reviews/{id}

## Promotions

- GET /promotions
- POST /admin/promotions

## Messages

- POST /messages
- GET /messages
- POST /admin/messages/{id}/reply

## Analytics

- GET /admin/analytics/overview
- GET /admin/analytics/sales
- GET /admin/analytics/best-sellers
- GET /admin/analytics/categories
- GET /admin/analytics/variants
- GET /admin/analytics/inventory

Add appropriate request/response schemas, validation, authentication, authorization, pagination, filtering, sorting, and HTTP status codes.

Document every endpoint in OpenAPI and in the project's API documentation.

---

# 13. FRONTEND DESIGN

Create a premium beauty e-commerce design.

## Design direction

- Warm white
- Soft blush pink
- Beige
- Neutral gray
- Charcoal
- Elegant typography
- High-quality product imagery
- Minimal layout
- Consistent spacing
- Responsive design
- Accessible forms and navigation

Avoid clutter, excessive animation, and inconsistent components.

## Customer pages

- Home
- Login
- Register
- Forgot Password
- Product Catalog
- Category
- Brand
- Search Results
- Product Details
- Cart
- Wishlist
- Checkout
- Payment Result
- Order Confirmation
- Order History
- Order Details
- Order Tracking
- Profile
- Address Management
- Reviews
- Customer Service
- Notifications
- About
- Contact
- Privacy Policy
- Terms and Conditions

## Admin pages

- Admin Login
- Dashboard
- Product Management
- Category Management
- Brand Management
- Variant Management
- Inventory Management
- Batch and Expiry Management
- Order Management
- Payment Management
- Customer Management
- Promotions
- Coupons
- Reviews
- Messages
- Notifications
- Analytics
- Reports
- Settings

Implement protected routes and role-based navigation.

Ensure all pages work on desktop, tablet, and mobile.

---

# 14. PROJECT STRUCTURE

Use a clean modular architecture similar to:

glowcart/
  frontend/
    src/
      assets/
      components/
      pages/
        customer/
        admin/
      layouts/
      hooks/
      services/
      store/
      routes/
      types/
      utils/
      App.tsx
      main.tsx
    package.json
    .env.example

  backend/
    app/
      api/
        v1/
      core/
      models/
      schemas/
      services/
      repositories/
      middleware/
      db/
      utils/
      main.py
    tests/
    alembic/
    requirements.txt
    .env.example

  docs/
    SRS.md
    architecture.md
    database-design.md
    api-specification.md
    user-stories.md
    use-cases.md
    development-roadmap.md
    testing-strategy.md
    deployment-guide.md
    user-manual.md
    installation-guide.md
    diagrams/
      system-architecture.mmd
      er-diagram.mmd
      use-case-diagram.mmd
      activity-diagram.mmd
      sequence-diagram.mmd

  docker-compose.yml
  .env.example
  .gitignore
  README.md
  DEVELOPMENT_STATUS.md
  CHANGELOG.md

You may improve the structure if necessary, but keep it modular and documented.

---

# 15. MANDATORY DOCUMENTATION REQUIREMENTS

Documentation is a major deliverable of this university project.

Do not treat documentation as an optional final task.

Create the following documents with meaningful, complete content.
-**Eveything you did should be recorded under/ docs/, that should include summary of the last thing you did as a context, summary of every phase should be recorded as well.
## A. README.md

Include:

1. Project name
2. Project overview
3. Project objectives
4. Main features
5. Technology stack
6. Architecture overview
7. Project folder structure
8. Prerequisites
9. Installation instructions
10. Environment variable setup
11. Database setup
12. Alembic migration instructions
13. Backend startup instructions
14. Frontend startup instructions
15. Test instructions
16. Demo account setup
17. API documentation URL
18. Deployment overview
19. Troubleshooting
20. Project limitations

Provide commands that match the actual project configuration.

## B. Software Requirements Specification — SRS.md

Write a formal SRS document containing:

1. Introduction
2. Purpose
3. Project scope
4. Intended users
5. Definitions and abbreviations
6. Overall system description
7. User classes and characteristics
8. Operating environment
9. Functional requirements
10. Non-functional requirements
11. External interface requirements
12. Software and hardware requirements
13. System constraints
14. Assumptions and dependencies
15. Acceptance criteria

Assign unique IDs to requirements, such as FR-001 and NFR-001.

## C. System Architecture — architecture.md

Include:

- System overview
- Three-tier architecture
- Frontend architecture
- Backend architecture
- Database architecture
- Authentication architecture
- Payment integration architecture
- Image storage architecture
- Deployment architecture
- Security architecture
- Data flow
- Major design decisions and trade-offs

Create architecture diagrams using Mermaid.

## D. Database Design — database-design.md

Include:

- Database overview
- All table descriptions
- Column names and data types
- Primary keys
- Foreign keys
- Unique constraints
- Check constraints
- Indexes
- Relationships
- One-to-one relationships
- One-to-many relationships
- Many-to-many relationships
- ER diagram
- Data dictionary
- Migration instructions

The ER diagram must match the actual SQLAlchemy models and migrations.

## E. API Specification — api-specification.md

For every API endpoint, document:

- HTTP method
- Endpoint path
- Purpose
- Authentication requirement
- Required role
- Path parameters
- Query parameters
- Request body
- Response body
- Status codes
- Validation rules
- Example request
- Example response
- Possible error responses

Ensure the documentation matches the actual FastAPI implementation.

## F. UML and System Diagrams

Create and maintain:

1. Use Case Diagram
2. Class Diagram
3. Activity Diagram
4. Sequence Diagram
5. Entity Relationship Diagram
6. System Architecture Diagram
7. Deployment Diagram
8. Data Flow Diagram

Use Mermaid source files where practical.

Include actors such as Customer, Admin, and Super Admin.

Diagrams must represent the implemented system, not an imaginary design.

## G. User Stories and Use Cases — user-stories.md and use-cases.md

Include:

- Customer registration
- Customer login
- Browse products
- Search products
- Select product variants
- Add to cart
- Checkout
- Make payment
- Track order
- Submit review
- Admin product management
- Admin inventory management
- Admin order management
- Admin sales analytics
- Super Admin user management

Include preconditions, main flow, alternative flow, and postconditions for important use cases.

## H. Installation Guide — installation-guide.md

Explain step by step:

- Required software
- Python environment setup
- Backend dependencies
- PostgreSQL setup
- Environment variables
- Database creation
- Alembic migrations
- Frontend dependencies
- Running the backend
- Running the frontend
- Running tests
- Common installation errors and fixes

Include commands for macOS and Windows where relevant.

## I. Deployment Guide — deployment-guide.md

Explain:

- Frontend deployment to Vercel
- Backend deployment to Railway
- PostgreSQL configuration
- Environment variables
- CORS configuration
- Cloudinary configuration
- Database migrations
- HTTPS
- Health checks
- Logging
- Backup considerations
- Troubleshooting
- Rollback considerations

Never expose real secrets in documentation.

## J. User Manual — user-manual.md

Write instructions for:

**Customers**
- Create an account
- Log in
- Browse products
- Search and filter
- Select shades and variants
- Add products to cart
- Apply coupons
- Checkout
- Make payment
- Track orders
- Submit reviews

**Administrators**
- Log in
- Add products
- Manage categories
- Manage brands
- Manage variants
- Upload images
- Receive stock
- Manage batches
- Check expiry alerts
- Process orders
- Manage payments
- Create promotions
- Review analytics
- Reply to customer messages

**Super Admin**
- Create administrators
- Assign roles
- Review audit logs
- Manage settings

## K. Testing Strategy — testing-strategy.md

Include:

- Testing objectives
- Unit testing
- Integration testing
- API testing
- Frontend testing
- Authentication testing
- Authorization testing
- Inventory testing
- Payment testing
- Order testing
- Security testing
- Performance testing
- User acceptance testing

Create a test case table with:

- Test ID
- Test scenario
- Preconditions
- Test steps
- Expected result
- Actual result
- Pass/Fail status

Do not mark tests as passed until they have actually been executed.

## L. Development Status — DEVELOPMENT_STATUS.md

Maintain this file throughout development.

For every phase, record:

- Phase name
- Tasks completed
- Tasks remaining
- Files created
- Files modified
- Database migrations
- API endpoints implemented
- Tests executed
- Test results
- Known bugs
- Blockers
- Next steps

Update this file after every major implementation milestone.

## M. Changelog — CHANGELOG.md

Record meaningful changes, including:

- New features
- Bug fixes
- Database changes
- API changes
- Security improvements
- Documentation changes

Use clear version entries.

---

# 16. UNIVERSITY FINAL PROJECT REPORT

Prepare a formal academic report based on the actual completed system.

Create the report in `docs/final-project-report.md`.

Use this chapter structure:

## Preliminary pages

- Title page
- Declaration placeholder
- Acknowledgement placeholder
- Abstract
- Table of Contents
- List of Figures
- List of Tables
- Abbreviations

Do not invent the student's name, university, supervisor, or institution. Use clearly labelled placeholders.

## Chapter 1 — Introduction

- Background
- Problem statement
- Project aim
- Project objectives
- Project scope
- Project significance
- Project limitations
- Organization of the report

## Chapter 2 — Literature Review

- Overview of e-commerce systems
- Cosmetic e-commerce platforms
- Inventory management systems
- Database management systems
- Web application technologies
- Existing system comparison
- Research gap
- Proposed solution

Use genuine references and provide citations. Never fabricate books, papers, authors, publication dates, or URLs. If references have not been verified, mark them for further research.

## Chapter 3 — Requirements Analysis

- Stakeholder analysis
- User requirements
- Functional requirements
- Non-functional requirements
- Hardware requirements
- Software requirements
- Use cases
- System constraints

## Chapter 4 — System Design

- System architecture
- Database design
- ER diagram
- UML diagrams
- User interface design
- API design
- Security design
- Data flow

## Chapter 5 — System Implementation

- Development environment
- Frontend implementation
- Backend implementation
- Database implementation
- Authentication implementation
- Product management
- Variant management
- Inventory management
- Order management
- Payment integration
- Analytics dashboard
- Deployment implementation

## Chapter 6 — Testing and Results

- Testing methodology
- Test environment
- Test cases
- Test results
- Screenshots of actual implementation
- Performance measurements
- Security test results
- Discussion

Only include results that were actually measured.

## Chapter 7 — Conclusion and Future Work

- Project summary
- Objectives achieved
- Project contributions
- Limitations
- Future improvements

## References and Appendices

Include:

- Verified references
- Installation guide
- API examples
- Database schema
- User manual
- Additional diagrams
- Selected code samples

Also create:

- `docs/abstract.md`
- `docs/presentation-outline.md`
- `docs/viva-questions.md`
- `docs/testing-report.md`

The viva document should include likely questions and technically correct answers about the architecture, database, security, API, inventory, payments, testing, and design decisions.

---

# 17. SECURITY AND QUALITY REQUIREMENTS

Implement:

- Secure password hashing
- JWT validation
- Role-based authorization
- Input validation
- SQL injection protection
- CORS configuration
- Rate limiting for sensitive endpoints
- Secure environment variables
- HTTPS in deployment
- Safe error handling
- Audit logging
- Secure file upload validation
- Payment verification
- Protection against duplicate transactions

Never commit `.env` files, passwords, tokens, or API secrets.

Use `.env.example` with placeholder values.

## Quality requirements

- Responsive interface
- Accessible forms and navigation
- Reusable frontend components
- Modular backend services
- Consistent error responses
- Database transaction integrity
- Pagination for large datasets
- Database indexes for common queries
- Optimized image loading
- Maintainable code
- Clear documentation

Performance targets must be measured under documented test conditions. Treat targets such as page load under 3 seconds and normal API p95 latency under 200 ms as goals, not guaranteed results.

---

# 18. TESTING REQUIREMENTS

Backend tests must cover:

- Registration
- Login
- Token refresh
- Role permissions
- Product CRUD
- Category CRUD
- Brand CRUD
- Variant management
- Inventory updates
- Expiry validation
- Cart operations
- Coupon validation
- Order creation
- Payment verification
- Duplicate webhook handling
- Review permissions
- Analytics calculations

Frontend tests must cover:

- Navigation
- Forms
- Authentication
- Protected routes
- Product filtering
- Variant selection
- Cart
- Checkout
- Admin pages

Important integration tests:

1. A customer cannot access admin endpoints.
2. An expired batch cannot be sold.
3. Stock cannot become negative.
4. Two simultaneous purchases cannot oversell the final available unit.
5. Repeated payment webhooks cannot create duplicate payment records.
6. Cancelled and refunded orders are handled correctly in revenue reports.
7. Historical order prices remain unchanged after catalog updates.

Run tests and record actual results in the documentation.

---

# 19. DEVELOPMENT PHASES

Follow these phases in order.

## Phase 1 — Repository Inspection and Planning

- Inspect repository.
- Identify existing files.
- Create implementation plan.
- Create SRS.
- Create architecture documentation.
- Create ERD.
- Create initial UML diagrams.
- Create development roadmap.

## Phase 2 — Project Setup

- Configure React and TypeScript.
- Configure Tailwind CSS.
- Configure FastAPI.
- Configure PostgreSQL.
- Configure SQLAlchemy.
- Configure Alembic.
- Configure environment variables.
- Configure Docker development environment.

## Phase 3 — Database and Authentication

- Create database models.
- Create migrations.
- Implement registration.
- Implement login.
- Implement JWT.
- Implement password hashing.
- Implement RBAC.
- Write tests.

## Phase 4 — Catalog and Product Management

- Create categories.
- Create brands.
- Create products.
- Create product images.
- Create variants.
- Implement search and filtering.
- Build admin product management.
- Write tests.

## Phase 5 — Inventory Management

- Implement inventory.
- Implement batches.
- Implement expiry management.
- Implement stock movement history.
- Implement stock alerts.
- Implement FEFO allocation.
- Write tests.

## Phase 6 — Customer Frontend

- Build homepage.
- Build catalog.
- Build product details.
- Build category and brand pages.
- Build authentication pages.
- Build responsive navigation.

## Phase 7 — Cart, Wishlist, Promotions, and Checkout

- Implement cart.
- Implement wishlist.
- Implement coupons.
- Implement promotions.
- Implement checkout.
- Connect frontend and backend.
- Write tests.

## Phase 8 — Orders and Payments

- Implement order creation.
- Implement order status workflow.
- Implement COD.
- Implement payment sandbox adapter.
- Implement payment verification.
- Implement payment history.
- Implement order tracking.
- Write tests.

## Phase 9 — Reviews and Customer Service

- Implement reviews.
- Implement notifications.
- Implement customer messages.
- Implement admin replies.
- Write tests.

## Phase 10 — Admin Dashboard and Analytics

- Build dashboard.
- Implement KPI APIs.
- Implement revenue charts.
- Implement product analytics.
- Implement variant analytics.
- Implement inventory reports.
- Implement report exports where appropriate.
- Write tests.

## Phase 11 — Security, Integration, and Performance

- Run full integration tests.
- Test role permissions.
- Test concurrency.
- Test payment idempotency.
- Test input validation.
- Review database queries.
- Measure performance.
- Fix issues.

## Phase 12 — Deployment and Final Documentation

- Prepare Vercel deployment.
- Prepare Railway deployment.
- Configure production PostgreSQL.
- Configure image storage.
- Prepare environment variable instructions.
- Run migrations.
- Verify health checks.
- Finalize README.
- Finalize SRS.
- Finalize architecture and ERD.
- Finalize API specification.
- Finalize user manual.
- Finalize installation and deployment guides.
- Finalize test report.
- Finalize academic report.
- Prepare presentation outline and viva questions.

---

# 20. ACCEPTANCE CRITERIA

The project is considered complete only when the following have been implemented and verified:

- Customer registration and login
- JWT authentication
- Role-based access control
- Product catalog
- Categories and brands
- Product variants
- Shade and volume selection
- Product search and filtering
- Shopping cart
- Wishlist
- Coupons and promotions
- Checkout
- Cash on Delivery
- Online payment sandbox
- Order management
- Order tracking
- Inventory management
- Batch and expiry management
- Stock movement history
- Reviews
- Customer service
- Notifications
- Admin dashboard
- Sales analytics
- Inventory analytics
- Responsive frontend
- Backend API tests
- Frontend tests
- Database migrations
- Deployment instructions
- Complete technical documentation
- Complete academic report draft

Create an acceptance checklist and mark each item only after verification.

---

# 21. FINAL AGENT INSTRUCTIONS

START NOW.

First inspect the current repository.

Then create the initial documentation and project plan.

After that, implement the application phase by phase.

Do not return only a proposal or code snippets.

Do not stop after creating folders.

Do not stop after creating the frontend.

Do not stop after creating the backend.

Do not stop after creating database models.

Continue until all feasible application features, tests, and documentation have been completed.

After each phase:

1. Summarize completed tasks.
2. List created and modified files.
3. Report database migrations.
4. Report implemented API endpoints.
5. Run relevant tests.
6. Show actual test results.
7. Fix errors.
8. Update `DEVELOPMENT_STATUS.md`.
9. Update affected documentation.
10. Continue to the next phase when acceptance criteria pass.

If you encounter an error, investigate and fix it instead of ignoring it.

If a third-party credential is unavailable, create the integration adapter, document the required credential, and continue working on the remaining features.

Never claim that deployment, payment integration, tests, or performance targets have succeeded unless they have actually been verified.

At the end, provide:

- Completed feature summary
- Final project architecture
- Database table summary
- API endpoint summary
- Testing results
- Known limitations
- Deployment instructions
- Documentation file list
- Remaining tasks, if any

**The final objective is a complete, functional, tested, well-documented GlowCart application suitable for university final-year project demonstration and academic evaluation.**