# Architecture

## Stack

| Layer | Tecnologia | Versão |
|---|---|---|
| Frontend | React + TypeScript + Vite | 19 / 5.8 / 6 |
| State | TanStack Query v5 + Zustand | — |
| Routing | React Router v6 (createBrowserRouter) | — |
| Charts | Recharts | — |
| Forms | React Hook Form + Zod | — |
| CSS | Design tokens (CSS custom properties) | — |
| Backend | Python + FastAPI + SQLAlchemy | 3.12 / 0.136 / 2.0 |
| Database | PostgreSQL | 16 |
| Queue | RabbitMQ | (preparado) |
| Auth | Keycloak + OAuth2-Proxy | 26.6 / 7.15 |
| Proxy | Traefik | 3.7 |
| Container | Docker Compose | — |
| Build | Bun (frontend) / pip (backend) | — |

## Estrutura de diretórios

```
saas/
├── frontend/                    # React SPA
│   ├── src/
│   │   ├── main.tsx            # Entry point (router, providers)
│   │   ├── pages/              # Route-level pages (lazy loaded)
│   │   ├── features/           # Feature modules (campaigns, channels, etc.)
│   │   ├── shared/             # Shared code
│   │   │   ├── api/            # client.ts, endpoints.ts, types.ts
│   │   │   ├── components/     # UI primitives (Button, Input, Badge, etc.)
│   │   │   ├── hooks/          # useAuth, useDebounce, useMediaQuery
│   │   │   ├── store/          # Zustand stores (authStore, uiStore)
│   │   │   └── utils/          # cn, date, number
│   │   └── styles/             # global.css (design tokens)
│   ├── nginx.conf              # Static SPA + /api/ proxy_pass
│   └── Dockerfile              # bun build → nginx
│
├── backend/                    # FastAPI
│   ├── src/
│   │   ├── main.py             # FastAPI app + middleware
│   │   ├── api/routers/        # Route handlers (auth, channels, contacts, etc.)
│   │   ├── middleware/         # ProxyAuthMiddleware, TenantMiddleware
│   │   ├── domain/             # Domain entities, value objects, exceptions
│   │   ├── application/        # Use cases (SendMessageUseCase, etc.)
│   │   └── infrastructure/     # Database engine, models, queue, settings
│   ├── alembic/                # DB migrations
│   ├── entrypoint.sh           # Startup: alembic upgrade + gunicorn
│   └── Dockerfile              # python:3.12-slim multi-stage
│
└── infra/                      # Infrastructure
    ├── docker-compose.yml      # All services
    ├── traefik/                # Traefik config (dynamic, middlewares)
    ├── oauth2-proxy/           # oauth2-proxy config template
    └── keycloak/               # Keycloak Dockerfile + realm template
```

## Multi-tenancy

### Modelo

Cada `Tenant` possui usuários, canais, contatos e mensagens próprios. O isolamento é feito via:

1. **`tenant_id` FK** em todas as tabelas de dados
2. **Row-Level Security (RLS)** no PostgreSQL — políticas aplicam `tenant_id = current_setting('app.current_tenant_id')::uuid`
3. **`request.state.tenant_id`** — setado pelo middleware e propagado para a sessão do DB via `set_config()`

### Resolução do tenant_id

O `ProxyAuthMiddleware` define `request.state.tenant_id` nesta ordem de prioridade:

1. **Header `X-Tenant-ID`** — override explícito (desenvolvimento)
2. **JWT claim `tenant_id`** — vindo do mapper do Keycloak (futuro)
3. **Database lookup** — busca `User` por `keycloak_user_id` (sub do JWT)
4. **Auto-provision** — se não encontrado, cria Tenant + User automaticamente

### Fluxo de dados do tenant

```
Middleware → request.state.tenant_id = "uuid"
                │
                ▼
get_db(request) → SELECT set_config('app.current_tenant_id', 'uuid', true)
                │
                ▼
Query → RLS policy: tenant_id = current_setting('app.current_tenant_id')::uuid
                │
                ▼
Resultado filtrado automaticamente pelo PostgreSQL
```

## Frontend

### Design System

Design tokens via CSS custom properties em `styles/global.css`:

```css
:root {
  --color-primary: #2563eb;
  --color-bg-base: #ffffff;
  --color-text-primary: #111827;
  --space-4: 1rem;
  --radius-md: 8px;
  --font-size-sm: 0.875rem;
  /* … */
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-bg-base: #1a1a2e;
    --color-text-primary: #f1f5f9;
    /* … */
  }
}
```

### Componentes

- **UI Primitives**: Button, Input, Badge, Modal, Spinner, EmptyState, StatCard
- **Layout**: AuthLayout, AppLayout (Sidebar + TopBar + responsive drawer)
- **Pages**: HomePage (pública), Dashboard, Campaigns, Contacts, Settings, Reports, etc.
- **AuthGuard**: Wrapper de rota que verifica `/api/v1/me` e redireciona para `/oauth2/sign_in` se não autenticado

### API Client

`shared/api/client.ts` — fetch wrapper:
- 401 → `window.location.href = '/oauth2/sign_in'`
- Erros → `ApiError` com status + body
- 204 → `undefined`
- JSON parse automático

## Backend

### Middleware stack

1. `ProxyAuthMiddleware` — extrai headers de auth, resolve tenant_id
2. (futuro) rate limiting, logging, CORS

### Rotas

| Prefixo | Router | Descrição |
|---|---|---|
| `/api/v1/health` | `health.py` | Health check (público) |
| `/api/v1/me` | `auth.py` | Info do usuário atual |
| `/api/v1/channels` | `channels.py` | CRUD de canais |
| `/api/v1/contacts` | `contacts.py` | Listagem de contatos |
| `/api/v1/messages` | `messages.py` | Envio e listagem de mensagens |
| `/api/v1/templates` | `templates.py` | (501 - não implementado) |
| `/healthz` | `health.py` | Health check interno |

### Dependências

- `require_tenant(request)` → retorna tenant_id ou 401
- `get_db(request)` → sessão SQLAlchemy com RLS configurado
- `get_producer()` → QueueProducer (RabbitMQ)

## Infraestrutura

### Docker Compose (`infra/docker-compose.yml`)

| Serviço | Imagem | Portas |
|---|---|---|
| traefik | traefik:v3.7 | 80, 443, 8080 (admin) |
| keycloak | keycloak:26.6 | 8080 (interno) |
| keycloak-db | postgres:16-alpine | — |
| oauth2-proxy | oauth2-proxy:v7.15 | 4180 (interno) |
| frontend | saas-frontend (build local) | 80 (interno) |
| backend | saas-backend (build local) | 8000 (interno) |
| app-db | postgres:16-alpine | — |

### Traefik routers

- `auth.localhost` → keycloak:8080
- `app.localhost` → oauth2-proxy:4180 (middleware: security-headers, rate-limit)
- `api.localhost` → backend:8000 (middleware: api-headers, oauth2-auth forward)

### Networks

- `proxy` — Traefik + serviços expostos
- `saas-internal` — comunicação interna entre serviços

## Estado atual (Jun 2026)

### Funcionando
- Autenticação completa via Keycloak + oauth2-proxy (PKCE)
- Auto-provisionamento de tenant na primeira autenticação
- CRUD de canais, listagem de contatos e mensagens
- Dashboard com estatísticas e gráficos
- Dark mode automático
- Builds multi-stage (bun → nginx, python → slim)

### Pendente
- Templates de mensagem (endpoint 501)
- Enfileiramento real com RabbitMQ
- Webhooks
- Onboarding formal (em vez de auto-provision)
- Keycloak mapper para `tenant_id` claim no JWT
