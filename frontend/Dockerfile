# Stage 1: Build
FROM oven/bun:canary-alpine@sha256:8e2c0cef20088df099bc360b15129df68945d3fec70e79b34ec5a252131a9b82 AS build

WORKDIR /app

COPY package.json bun.lock ./
RUN bun install --frozen-lockfile --production && \
    bun install --frozen-lockfile --dev

COPY tsconfig.json tsconfig.node.json vite.config.ts ./
COPY public/ public/
COPY src/ src/
COPY index.html ./

RUN bun run build

# Stage 2: Runtime
FROM nginx:stable-alpine@sha256:5f979dcfed4ce6461873f087e8c980d6e29b084b9e8776d9704a7e989b5f4898

RUN apk add --no-cache ca-certificates tzdata && \
    addgroup --system --gid 1001 app && \
    adduser --system --uid 1001 --ingroup app app && \
    mkdir -p /usr/share/nginx/html && \
    chown app:app /usr/share/nginx/html && \
    touch /var/run/nginx.pid && \
    chown app:app /var/run/nginx.pid && \
    chown -R app:app /var/cache/nginx && \
    rm -rf /etc/nginx/conf.d/* /usr/share/nginx/html/*

COPY --from=build --chown=app:app /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

RUN chmod 644 /etc/nginx/nginx.conf && \
    chmod -R 755 /usr/share/nginx/html

USER app
EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=5s \
  CMD wget --quiet --tries=1 --spider http://localhost:80/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
