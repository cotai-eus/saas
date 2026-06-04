# Auth Flow

Autenticação via **Keycloak OIDC** + **OAuth2-Proxy** com PKCE (S256).

## Topologia

```
Browser ──HTTPS──▶ Traefik (443)
                      │
                      ├── auth.localhost ──▶ Keycloak (8080)
                      │
                      └── app.localhost ──▶ oauth2-proxy (4180)
                                               │
                                               ▼ (reverse proxy)
                                          frontend nginx (80)
                                               │
                                          ┌────┴────┐
                                          │         │
                                          ▼         ▼
                                      SPA (/)   /api/ ──▶ backend (8000)
```

O router `frontend` no Traefik (`docker-compose.yml`) aponta para o **service `oauth2-proxy`**, não para o nginx diretamente. Todo o tráfego de `app.localhost` passa pelo oauth2-proxy.

## Fluxo de autenticação

### 1. Requisição não autenticada

1. Browser acessa `https://app.localhost/dashboard`
2. Traefik roteia para o service `oauth2-proxy`
3. OAuth2-Proxy não encontra cookie de sessão (`_oauth2_proxy`)
4. Retorna **302** para `https://auth.localhost/realms/saas/protocol/openid-connect/auth?…`
5. Browser segue o redirect para Keycloak
6. Keycloak apresenta formulário de login
7. Usuário faz login (usuário `test-user` / senha definida no realm)
8. Keycloak gera `authorization_code` e redireciona para `/oauth2/callback?code=…&state=…`
9. OAuth2-Proxy troca o código por tokens (PKCE S256)
10. Cria sessão, seta cookie `_oauth2_proxy` (SameSite=None, Secure)
11. Redireciona para `/` (dashboard)

### 2. Requisição autenticada

1. Browser envia requisição com cookie `_oauth2_proxy`
2. OAuth2-Proxy valida a sessão
3. Proxy reverso para `http://frontend:80` adicionando headers:
   - `X-Auth-Request-User` — prefered_username do Keycloak (ex: `test-user`)
   - `X-Auth-Request-Email` — email do Keycloak (ex: `test@localhost`)
   - `X-Auth-Request-Groups` — grupos do usuário
   - `Authorization: Bearer <access_token>` — JWT do Keycloak
4. Nginx serve SPA ou proxy reverso `/api/` → `backend:8000` propagando os headers

### 3. Resolução de tenant_id (backend)

O middleware `ProxyAuthMiddleware` (`backend/src/middleware/auth.py`) executa em toda requisição:

```
request.headers → X-Auth-Request-User, X-Auth-Request-Email, Authorization
                              │
                              ▼
                    jwt.get_unverified_claims(token)
                              │
                    ┌─────────┴──────────┐
                    │                    │
               tenant_id          tenant_id null
               presente?          + sub presente?
                    │                    │
                   usa              consulta DB
                                    keycloak_user_id
                                          │
                              ┌───────────┴───────────┐
                              │                       │
                          usuário                 não encontrado
                          existe?                  (auto-provision)
                              │                       │
                          retorna               cria Tenant + User
                          tenant_id             retorna tenant_id
```

**Auto-provisionamento**: Na primeira requisição de um usuário novo, o middleware:
1. Cria um `Tenant` com nome baseado no email (`test's Workspace`) e slug único
2. Cria um `User` vinculado ao tenant com `keycloak_user_id = sub` do JWT
3. Persiste no banco e retorna o `tenant_id`

Requisições subsequentes encontram o usuário no banco e usam o `tenant_id` já existente.

## Headers de autenticação

| Header | Origem | Exemplo |
|---|---|---|
| `X-Auth-Request-User` | oauth2-proxy (set_xauthrequest) | `test-user` |
| `X-Auth-Request-Email` | oauth2-proxy | `test@localhost` |
| `X-Auth-Request-Groups` | oauth2-proxy | `/app-users` |
| `Authorization: Bearer …` | oauth2-proxy (pass_access_token) | JWT do Keycloak |
| `X-Tenant-ID` | (opcional, dev override) | UUID |

## Cookies

| Cookie | Domínio | SameSite | Finalidade |
|---|---|---|---|
| `_oauth2_proxy` | `app.localhost` | `None` | Sessão do oauth2-proxy |
| `_oauth2_proxy_csrf` | `app.localhost` | `None` | CSRF (por requisição) |
| `KEYCLOAK_SESSION` | `auth.localhost` | `Lax` | Sessão do Keycloak |
| `KEYCLOAK_IDENTITY` | `auth.localhost` | `Lax` | Identity do Keycloak |

`SameSite=None` é necessário porque o callback OAuth cruza domínios (auth.localhost → app.localhost).
`cookie_domains` foi removido porque `.localhost` é rejeitado por alguns browsers com `SameSite=None`.

## Configurações do oauth2-proxy

```ini
upstreams = ["http://frontend:80"]
reverse_proxy = true
set_xauthrequest = true
pass_access_token = true
pass_authorization_header = true
set_authorization_header = true
code_challenge_method = "S256"
cookie_samesite = "none"
cookie_csrf_per_request = true
skip_auth_routes = ["^/healthz$", "^/metrics$", "^/api/public/.*"]
```

## Histórico de problemas resolvidos

### Problema 1: CSP bloqueando API calls

- **Sintoma**: Console do navegador mostrava erro de CSP bloqueando fetch para `/api/v1/channels`
- **Causa**: FastAPI com `redirect_slashes=True` (padrão) retornava 307 redirect de `/api/v1/channels` para `/api/v1/channels/`. O nginx rewrite do Location usava `http://` (scheme do proxy interno), e CSP `connect-src 'self'` bloqueava o HTTP.
- **Solução**: `redirect_slashes=False` no FastAPI + rotas `@router.get("")` em vez de `@router.get("/")`

### Problema 2: Loop de re-autenticação infinita

- **Sintoma**: Browser logava repetidamente: `/api/v1/me (200)` → `/api/v1/channels (401)` → redirect `/oauth2/sign_in` → callback → `/api/v1/me (200)` → loop
- **Causa**: O middleware extraía `tenant_id` do JWT (`claims.get("tenant_id")`), mas Keycloak não tem mapper para esse claim → `tenant_id` sempre null → `require_tenant()` retornava 401 em todas as rotas protegidas
- **Solução**: Adicionado fallback de consulta ao banco: quando `tenant_id` é nulo, busca usuário por `keycloak_user_id` (sub do JWT). Se não existir, auto-provisiona tenant + user.

### Problema 3: `t is not iterable` no Dashboard

- **Sintoma**: "Unexpected Application Error! t is not iterable" ao carregar dashboard
- **Causa**: Backend retornava `{"total": 0, "items": []}` (resposta paginada) mas frontend esperava array simples `[]`
- **Solução**: List endpoints alterados para retornar array diretamente: `channels`, `contacts`, `messages`

### Problema 4: Forward auth vs Reverse proxy

- **Sintoma**: Forward auth retornava 401 raw para o browser sem redirect
- **Causa**: Forward auth mode devolve 401 para o proxy (Traefik), que não sabe fazer redirect OIDC
- **Solução**: Mudado para reverse proxy mode: Traefik roteia `app.localhost` para o service `oauth2-proxy`, que gerencia sessão e redirects

### Problema 5: Sem migrations no container

- **Sintoma**: Backend saudável mas rotas retornavam `relation "users" does not exist`
- **Causa**: Dockerfile não copiava `alembic/` nem `alembic.ini`
- **Solução**: Adicionado `COPY` para alembic + entrypoint.sh que executa `alembic upgrade head` antes do gunicorn

## Rotas públicas vs protegidas

| Rota | Auth necessária | Handler |
|---|---|---|
| `/api/v1/me` | Não (retorna null) | `me()` em `auth.py` |
| `/api/v1/health` | Não | `health.py` |
| `/api/v1/channels` | Sim (require_tenant) | `channels.py` |
| `/api/v1/contacts` | Sim | `contacts.py` |
| `/api/v1/messages` | Sim | `messages.py` |
| `/api/v1/templates` | Sim | `templates.py` (501) |
