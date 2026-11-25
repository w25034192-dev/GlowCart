# Installation Guide — GlowCart

## 1. Required Software
- **Python:** 3.12+
- **Node.js & npm:** Node 20 LTS+
- **PostgreSQL:** 15+ (macOS: `Postgres.app` or Homebrew `postgresql@16`; Windows: PostgreSQL 16 Installer)
- **Git** (optional for version control)

## 2. Backend Setup (macOS / Linux)
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Windows (PowerShell)
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

## 3. PostgreSQL & Environment Variables
1. Create a database named `glowcart` and user `glowcart_user` in PostgreSQL.
2. Update `backend/.env`:
   - `DATABASE_URL=postgresql+psycopg://glowcart_user:YOUR_PASSWORD@localhost:5432/glowcart`
   - `JWT_SECRET_KEY=<at-least-32-random-characters>`
   - `PAYMENT_WEBHOOK_SECRET=<random-hmac-secret>`

## 4. Alembic Migrations & Demo Seed
```bash
cd backend
alembic upgrade head
python3 -m app.db.seed
```

## 5. Run Backend Server
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```
OpenAPI docs will be available at `http://localhost:8000/docs`.

## 6. Frontend Setup & Startup
```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```
The storefront will be served at `http://localhost:5173`.

## 7. Running Tests
```bash
# Backend Pytest suite
cd backend && python3 -m pytest tests -v

# Frontend Vitest suite (requires Node.js 20+)
cd frontend && npm test
```

## 8. Common Errors & Fixes
- **`psycopg` connection error:** Confirm PostgreSQL is running on port `5432` and credentials match `DATABASE_URL`.
- **401 / CORS error in browser:** Ensure `CORS_ORIGINS` in `backend/.env` includes `http://localhost:5173`.

