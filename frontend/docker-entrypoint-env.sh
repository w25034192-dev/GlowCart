#!/bin/sh
set -eu

API_URL="${VITE_API_BASE_URL:-${API_BASE_URL:-${BACKEND_PUBLIC_URL:-}}}"
ESCAPED_URL=$(printf '%s' "$API_URL" | tr -d '\r\n' | sed 's/\\/\\\\/g; s/"/\\"/g')

cat > /tmp/env-config.js <<EOF
window.__GLOWCART_CONFIG__ = {
  VITE_API_BASE_URL: "${ESCAPED_URL}"
};
EOF
