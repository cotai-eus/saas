# saas-frontend

React 19 + TypeScript SPA servida por Nginx (multi-stage Docker).

## Scripts

```bash
npm run dev        # Vite dev server (porta 5173)
npm run build      # tsc + Vite build → dist/
npm test           # Vitest
```

## Docker

```bash
docker build -t saas-frontend .
docker run -p 80:80 saas-frontend
```

Acessível em `https://app.{domain}` via Traefik.

O container usa usuário não-root `app` (UID 1001) e nginx customizado com `pid` e caches em `/tmp`.

## Stack

- React 19 · TypeScript 5.8 · Vite 6
- Vitest + Testing Library + jsdom
- Nginx stable-alpine
