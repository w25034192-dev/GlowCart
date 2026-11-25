#!/bin/sh
set -eu

echo "Running Alembic database migrations..."
python -m alembic upgrade head

if [ "${SEED_DEMO_DATA:-false}" = "true" ]; then
  echo "Seeding demo catalog data..."
  python -m app.db.seed --generate-100
fi

PORT_VALUE="${PORT:-8000}"
echo "Starting GlowCart FastAPI server on port ${PORT_VALUE}..."
exec uvicorn app.main:app \
  --host 0.0.0.0 \
  --port "${PORT_VALUE}" \
  --proxy-headers \
  --forwarded-allow-ips="*"

