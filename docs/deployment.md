# Deployment

## Pré-requisitos

- Docker + Docker Compose v2
- Domínios DNS apontando para o servidor (ou `/etc/hosts` para dev):
  - `app.localhost` — frontend + SPA
  - `auth.localhost` — Keycloak
  - `api.localhost` — backend (opcional, rota direta)
- Portas 80 e 443 acessíveis

## Desenvolvimento local

### 1. Configurar hosts

```bash
echo '127.0.0.1 app.localhost auth.localhost api.localhost' | sudo tee -a /etc/hosts
```

### 2. Gerar secrets (primeira vez)

```bash
go run tools/ctl/main.go genenv
```

### 3. Subir tudo

```bash
docker compose -f infra/docker-compose.yml up -d --build
```

### 4. Verificar

```bash
# Todos os serviços saudáveis?
docker compose -f infra/docker-compose.yml ps

# Health check do backend
curl -k https://api.localhost/healthz

# Login via browser
open https://auth.localhost    # Keycloak admin (admin / senha do .env)
open https://app.localhost     # App (login via Keycloak)
```

### 5. Logs

```bash
docker compose -f infra/docker-compose.yml logs -f backend
docker compose -f infra/docker-compose.yml logs -f oauth2-proxy
docker compose -f infra/docker-compose.yml logs -f frontend
```

## Rebuild de serviço específico

```bash
# Backend apenas
docker compose -f infra/docker-compose.yml up -d --build backend

# Frontend apenas
docker compose -f infra/docker-compose.yml up -d --build frontend
```

## Migrations

As migrations rodam automaticamente no startup do backend via `entrypoint.sh`:

```bash
#!/bin/sh
set -e
alembic upgrade head
exec gunicorn src.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

Para rodar manualmente:

```bash
docker compose -f infra/docker-compose.yml exec backend alembic upgrade head
```

## Estrutura de build

### Frontend (multi-stage)

```
Stage 1 (builder): oven/bun:1-alpine
  ├── bun install --frozen-lockfile
  └── bun run build (tsc + vite)

Stage 2 (runtime): nginx:stable-alpine
  ├── copia dist/ do builder
  ├── copia nginx.conf
  └── user app (non-root, uid 1001)
```

### Backend (multi-stage)

```
Stage 1 (builder): python:3.12-slim
  ├── pip install .
  └── /opt/venv/

Stage 2 (runtime): python:3.12-slim
  ├── copia /opt/venv/ do builder
  ├── copia src/
  ├── copia alembic.ini + alembic/
  ├── copia entrypoint.sh
  └── user app (non-root, uid 1001)
```

## Variáveis de ambiente

Arquivo: `infra/.env` (gerado por `tools/ctl genenv`)

| Variável | Descrição | Exemplo |
|---|---|---|
| `APP_HOST` | Host do frontend | `app.localhost` |
| `AUTH_HOST` | Host do Keycloak | `auth.localhost` |
| `BASE_DOMAIN` | Domínio base | `localhost` |
| `OAUTH2_PROXY_CLIENT_ID` | Client ID no Keycloak | `oauth2-proxy` |
| `OAUTH2_PROXY_CLIENT_SECRET` | Client secret | (hex) |
| `OAUTH2_PROXY_COOKIE_SECRET` | Secret do cookie | (hex 32 bytes) |
| `SAAS_API_CLIENT_SECRET` | Client secret da API | (hex) |
| `DATABASE_URL` | URL do PostgreSQL (app) | `postgresql://saas:...@app-db:5432/saas` |
| `KC_DB_PASSWORD` | Senha do DB do Keycloak | (hex) |
| `KC_ADMIN_PASSWORD` | Senha do admin do Keycloak | (hex) |
| `OAUTH2_PROXY_SSL_INSECURE` | Skip SSL verify (dev) | `true` |

## Keycloak realm

Importado automaticamente no primeiro startup via template `infra/keycloak/templates/realm-template.json`.

O template é renderizado com `sed` no startup:

```bash
sed -e 's|${AUTH_HOST}|...|g' -e 's|${APP_HOST}|...|g' \
  realm-template.json > /opt/keycloak/data/import/realm-saas.json
```

### Usuário de teste

- Username: `test-user`
- Email: `test@localhost`
- Senha: definida no realm template
- Grupos: `/app-users`
- Roles: `user`

## Verificação pós-deploy

### 1. Backend health

```bash
curl -k https://api.localhost/healthz
# OK
```

### 2. Auth flow

Abrir `https://app.localhost` no browser:
- Deve redirecionar para Keycloak
- Login com `test-user`
- Deve redirecionar de volta para o dashboard
- Dashboard deve mostrar "Bom dia, test" e cards com dados

### 3. API autenticada

```bash
# Logar no browser, copiar cookie _oauth2_proxy, usar:
curl -k -b '_oauth2_proxy=...' https://app.localhost/api/v1/me
# {"user_id":"...","email":"test@localhost","tenant_id":"...","roles":[],"groups":[]}

curl -k -b '_oauth2_proxy=...' https://app.localhost/api/v1/channels
# []
```

## Troubleshooting

### Loop de login

**Sintoma**: Browser fica redirecionando entre app.localhost e auth.localhost indefinidamente.

**Causas**:
- `tenant_id` não resolvido (verificar logs do backend: `docker logs saas-backend`)
- Cookie CSRF expirado ou bloqueado (verificar se `cookie_samesite = "none"`)
- Sessão do Keycloak expirada mas cookie do oauth2-proxy ainda vivo

**Solução**:
1. Limpar cookies do browser para `app.localhost`
2. Verificar logs: `docker compose logs oauth2-proxy | grep -E "AuthSuccess|sign_in"`
3. Verificar se o auto-provision rodou: `docker compose logs backend | grep "Auto-provisioned"`

### CSP bloqueando requisições

**Sintoma**: Console do browser mostra `Content Security Policy: The page's settings blocked the loading of a resource at …`

**Causa**: Traefik middleware `security-headers` injeta CSP que precisa ser atualizada.

**Solução**: Adicionar domínios necessários em `infra/traefik/config/middlewares.yml`:

```yaml
security-headers:
  headers:
    contentSecurityPolicy: "connect-src 'self' https://fonts.googleapis.com https://fonts.gstatic.com; …"
```

### 401 em todas as rotas

**Sintoma**: `/api/v1/me` retorna 200 mas `/api/v1/channels` retorna 401.

**Causa**: `tenant_id` não resolvido — usuário não existe no banco e auto-provision falhou.

**Solução**: Verificar logs do backend. Se a tabela `users` não existir, rodar migrations manualmente:

```bash
docker compose exec backend alembic upgrade head
```
