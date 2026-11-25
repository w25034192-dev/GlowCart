# syntax=docker/dockerfile:1

FROM node:20-alpine AS dev

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]

# Build static production bundle (pass VITE_API_BASE_URL as build arg on Railway/Docker)
FROM dev AS builder

ARG VITE_API_BASE_URL=http://localhost:8000/api/v1
ARG VITE_APP_NAME=GlowCart

ENV VITE_API_BASE_URL=$VITE_API_BASE_URL \
    VITE_APP_NAME=$VITE_APP_NAME

RUN npm run build

# Hardened non-root production Nginx stage (default target for Railway)
FROM nginxinc/nginx-unprivileged:1.27-alpine AS production

ENV PORT=8080

COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY docker-entrypoint-env.sh /docker-entrypoint.d/99-glowcart-env.sh
RUN chmod +x /docker-entrypoint.d/99-glowcart-env.sh
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -qO- "http://127.0.0.1:${PORT}/healthz" || exit 1

