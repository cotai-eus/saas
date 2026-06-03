# SaaS Platform — Ambiente de Desenvolvimento Local

Stack: **Traefik v3.7** · **Keycloak v26.6** · **OAuth2-Proxy v7.15** · **PostgreSQL 16** · **Python/FastAPI** · **React 19 / Vite**

---

## Arquitetura

```
Internet / Browser
        │
        ▼
  ┌──────────────────────────────────────────┐
  │           TRAEFIK v3.7                   │
  │  Reverse Proxy / API Gateway             │
  │  :80 → redirect HTTPS                    │
  │  :443 → TLS termination                  │
  └────┬──────────┬──────────┬───────────────┘
       │          │          │
       ▼          ▼          ▼
  auth.{d}    app.{d}    api.{d}
  (Keycloak)  (Frontend) (Backend)
       │          │          │
       │          │    ForwardAuth
       │          │          │
       │          │    ┌────▼────────┐
       │          │    │ OAUTH2-PROXY│
       │          │    │   v7.15     │
       │          │    └────┬────────┘
       │          │         │ OIDC
       ▼          ▼         ▼
  ┌──────────────────────────────┐
  │        KEYCLOAK v26.6        │
  │     IdP / OIDC / realm: saas │
  └──────────┬───────────────────┘
             │
    ┌────────┴────────┐
    ▼                 ▼
  PG DBs          FastAPI
  (keycloak       (Backend)
   + app)            │
                     ▼
                  React SPA
                  (Frontend, Nginx)
```

### Fluxo de Autenticação

```
1. Usuário acessa https://app.{domain} (Frontend React SPA)
2. Frontend faz chamadas AJAX para https://api.{domain} (Backend FastAPI)
3. Traefik → middleware oauth2-auth → ForwardAuth para oauth2-proxy:4180
4. Sem cookie de sessão → redirect para https://auth.{domain}/realms/saas/...
5. Keycloak autentica (login, MFA, etc.)
6. Código de autorização → redirect para /oauth2/callback
7. OAuth2-Proxy troca código por tokens (ID + Access)
8. Cookie de sessão criado → redirect para api.{domain}
9. Traefik injeta headers X-Auth-Request-* no request
10. Backend FastAPI recebe JWT validado com info do usuário
```

### Rotas e Serviços

| Domínio | Serviço | Middleware | Descrição |
|---|---|---|---|
| `traefik.{domain}` | Dashboard Traefik | basic-auth | Monitoramento do proxy |
| `auth.{domain}` | Keycloak | security-headers | Identity Provider (OIDC) |
| `app.{domain}` | Nginx (React SPA) | security-headers + rate-limit | Frontend React |
| `api.{domain}` | FastAPI (Backend) | oauth2-auth + security-headers | API SaaS protegida |
| `/oauth2/*` | OAuth2-Proxy | — | Callback OIDC |

---

## Stack

### Infraestrutura
- **Traefik** — reverse proxy com TLS, Let's Encrypt, e pipeline de middlewares (auth, security headers, rate-limit, CORS)
- **Keycloak** — IdP OIDC com realm `saas`, clientes `oauth2-proxy` (web) e `saas-api` (machine-to-machine), brute-force protection, grupos e roles
- **OAuth2-Proxy** — proxy de autenticação OIDC que valida sessões e injeta headers de identidade
- **PostgreSQL 16** — dois bancos isolados na rede `internal` (keycloak-db + app-db)

### Aplicação
- **Backend** — Python/FastAPI com validação JWT (RS256, JWKS cache), SQLAlchemy + Alembic, multi-tenant via Row-Level Security do PostgreSQL
- **Frontend** — React 19 + TypeScript + Vite 6, servido por Nginx (multi-stage build)

### CLI (Go)
- **`ctl`** — CLI em Go com Cobra + Bubbletea TUI para setup e gerenciamento do stack
- Gera CA própria + certificado wildcard `*.{domain}`
- Cria `.env` com segredos aleatórios
- Orquestra Docker Compose (up, down, logs, status, clean)

---

## Pré-requisitos

```bash
docker --version       # Docker + Compose v2
go version             # Go 1.22+ (para compilar o CLI)
mkcert                # opcional — o CLI gera seus próprios certificados
```

---

## Setup Rápido

```bash
# 1. Compila o CLI
make build

# 2. Setup interativo (CA, certificados, .env, rede Docker)
make setup

# 3. Sobe o stack completo
make up
make status
```

O comando `make setup` executa o TUI interativo que:
1. Solicita o domínio (default: `local.dev`)
2. Pergunta o ambiente (dev, staging, prod)
3. Oferece backup de arquivos existentes
4. Gera CA ECDSA P-256 + certificado wildcard
5. Gera `.env` com senhas aleatórias
6. Cria a rede Docker `proxy`

Para CI/CD:

```bash
make setup-ci   # equivalente a: ./ctl setup --no-interactive
```

---

## Comandos

| Comando | Descrição |
|---|---|
| `make build` ou `make build-linux` | Compila o CLI Go → `./ctl` |
| `make setup` | Setup interativo do ambiente |
| `make up` | Sobe todos os serviços |
| `make down` | Para todos os serviços |
| `make logs` | Logs do stack |
| `make status` | Status dos serviços |
| `make clean` | Remove containers |
| `make clean-all` | Remove containers, volumes e certificados |
| `make restart` | Reinicia o stack |
| `./ctl logs <service>` | Logs de um serviço específico |

Também é possível usar o binário diretamente:

```bash
./ctl setup --domain example.com --env prod --no-interactive
./ctl up
./ctl status
```

---

## Estrutura do Projeto

```
saas/
├── Makefile                        # Targets: build, setup, up, down, logs, status, clean
├── ctl                             # CLI compilado (Go)
│
├── infra/
│   ├── docker-compose.yml          # Orquestração dos 6 serviços
│   ├── .env                        # Segredos (não versionar)
│   ├── traefik/
│   │   ├── traefik.yml             # Config estática (entrypoints, TLS, providers)
│   │   ├── certs/                  # CA + wildcard (gerados pelo setup)
│   │   └── config/
│   │       ├── middlewares.yml     # Config dinâmica (auth, headers, rate-limit)
│   │       └── .htpasswd           # BasicAuth do dashboard
│   ├── keycloak/
│   │   └── realm-template.json     # Realm OIDC com envsubst
│   └── oauth2-proxy/
│       └── oauth2-proxy.cfg.tmpl   # Config template com envsubst
│
├── backend/                        # Python / FastAPI
│   ├── Dockerfile                  # python:3.12-slim, usuário não-root
│   ├── pyproject.toml              # FastAPI, SQLAlchemy, Alembic, python-jose
│   ├── alembic/                    # Migrations (001_initial_schema com RLS)
│   └── src/
│       ├── main.py                 # FastAPI app com JWKS middleware
│       ├── api/routers/            # health, auth (/me)
│       ├── middleware/             # JWT auth + tenant context
│       ├── domain/                 # Entidades de domínio
│       ├── application/            # Casos de uso
│       └── infrastructure/
│           ├── settings.py         # Config via pydantic-settings
│           └── database/
│               ├── models/         # Tenant, User, Subscription, AuditLog, Session, APIKey, FeatureFlag
│               ├── session.py      # Engine + scoped session com RLS
│               └── base.py         # DeclarativeBase
│
├── frontend/                       # React 19 / Vite / TypeScript
│   ├── Dockerfile                  # Multi-stage: node:20-alpine → nginx:stable-alpine
│   ├── package.json                # React 19, Vite 6, Vitest, Testing Library
│   └── src/
│       ├── main.tsx                # Entry point React 19
│       └── App.tsx                 # Componente inicial
│
└── tools/ctl/                      # Go CLI (Cobra + Bubbletea + Lipgloss)
    ├── main.go
    ├── cmd/                        # root, setup, up, down, logs, status, clean
    └── internal/
        ├── setup/                  # Orquestração do setup
        ├── tui/                    # Bubbletea TUI interativo
        ├── cert/                   # Geração CA + wildcard ECDSA
        ├── env/                    # Geração .env com .env.example embutido
        ├── secrets/                # Geração de segredos cripto-aleatórios
        ├── backup/                 # Backup com rotação de arquivos
        └── infra/                  # Docker network + docker compose executor
```

---

## Segurança

### Implementado
- ✅ TLS obrigatório (HTTP → HTTPS automático)
- ✅ CA própria + wildcard `*.{domain}`
- ✅ Headers OWASP (HSTS, CSP, X-Frame-Options, etc.)
- ✅ Rede `internal` isolada (bancos inacessíveis externamente)
- ✅ Docker socket read-only
- ✅ `exposedByDefault: false` (princípio do menor privilégio)
- ✅ Segredos injetados via ambiente (não hard-coded)
- ✅ Rate limiting (100 req/min, burst 50)
- ✅ Brute-force protection (5 falhas → 900s bloqueio)
- ✅ Cookies HttpOnly + Secure + SameSite=Lax
- ✅ Headers sensíveis removidos dos logs de acesso
- ✅ Validação JWT com JWKS cache
- ✅ Multi-tenant via RLS do PostgreSQL
- ✅ Senhas com política de 12+ caracteres

### Para produção
- [ ] Let's Encrypt (`TLS_RESOLVER=letsencrypt` + email)
- [ ] `OAUTH2_PROXY_SSL_INSECURE=false`
- [ ] `KC_HOSTNAME_STRICT: "true"` (já configurado)
- [ ] Secrets gerenciados por Vault ou Docker Secrets
- [ ] MFA obrigatório no Keycloak
- [ ] Restrição de `email_domains` no oauth2-proxy
- [ ] Backup automático dos volumes

---

## Desenvolvimento

### Backend
```bash
cd backend
pip install -e ".[dev]"
uvicorn src.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Testes
```bash
make test                    # ou individualmente:
cd backend && pytest -v      # Python/FastAPI
cd frontend && npm test      # React/Vitest
cd tools/ctl && go test ./... -v  # Go CLI
```

### CI/CD
O repositório inclui workflows GitHub Actions:
- **CI** — testes e lint nos 3 projetos (Python, Go, React)
- **CD** — deploy automatizado para staging/production
- **Security** — scan de segurança (placeholder)

---

## Troubleshooting

**`ERR_CERT_AUTHORITY_INVALID` no browser**
```bash
sudo cp infra/traefik/certs/rootCA.pem /usr/local/share/ca-certificates/
sudo update-ca-certificates
# Reinicie o browser
```

**OAuth2-Proxy retorna `500`**
```bash
./ctl logs oauth2-proxy
# Verifique OAUTH2_PROXY_CLIENT_SECRET e se Keycloak está healthy
```

**Keycloak não inicia**
```bash
./ctl logs keycloak-db   # verifica o banco
./ctl up                 # tenta novamente
```

**ForwardAuth retorna 401**
```bash
./ctl logs oauth2-proxy | grep -i "error\|invalid\|failed"
# Cookie domain deve cobrir .{domain} (com ponto inicial)
```
