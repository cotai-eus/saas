# SaaS Local — Guia de Configuração
## Stack: Traefik v3.7 · Keycloak v26.6 · OAuth2-Proxy v7.15 · Go CLI

---

## Visão Geral da Arquitetura

```
Internet / Browser
        │
        ▼
  ┌──────────────────────────────────────────┐
  │           TRAEFIK v3.7                   │
  │  (Reverse Proxy / API Gateway)           │
  │  :80 → redirect HTTPS                    │
  │  :443 → TLS termination                  │
  └───┬──────────┬──────────┬────────────────┘
      │          │          │
      ▼          ▼          ▼
  auth.local  app.local  api.local
      │          │          │
      │       ForwardAuth   │
      │          │          │
      │     ┌────▼────────┐ │
      │     │ OAUTH2-PROXY│ │
      │     │   v7.15     │ │
      │     └────┬────────┘ │
      │          │ OIDC     │
      ▼          ▼          │
  ┌──────────────────────┐  │
  │   KEYCLOAK v26.6     │  │
  │   (IdP / OIDC)       │◄─┘ JWT validation
  │   realm: saas-local  │
  └──────────────────────┘
      │          │
  ┌───▼───┐  ┌──▼──────────────┐
  │  PG   │  │  app1   app2    │
  │  DB   │  │  (suas apps)    │
  └───────┘  └─────────────────┘
```

### Fluxo de Autenticação (Browser)

```
1. Usuário acessa https://app.local.dev
2. Traefik chama oauth2-proxy via ForwardAuth (middleware)
3. OAuth2-Proxy verifica cookie de sessão
   → Não existe: redireciona para https://auth.local.dev/realms/saas-local/...
4. Keycloak autentica o usuário (login/senha, MFA, etc.)
5. Keycloak emite código de autorização → redireciona para /oauth2/callback
6. OAuth2-Proxy troca o código por tokens (ID token, Access token)
7. OAuth2-Proxy cria cookie de sessão e redireciona para a app
8. Traefik injeta headers X-Auth-Request-* no request para a app
9. App recebe requisição autenticada com dados do usuário
```

---

## Pré-requisitos

```bash
# Docker
docker --version

# Go (para compilar o CLI)
go version

# mkcert (opcional, o CLI gera certificados próprios)
# macOS
brew install mkcert
# Ubuntu/Debian
sudo apt install libnss3-tools
curl -fsSL https://github.com/FiloSottile/mkcert/releases/latest/download/mkcert-v*-linux-amd64 \
  -o /usr/local/bin/mkcert && chmod +x /usr/local/bin/mkcert
```

---

## Setup Inicial

### 1. Compile o CLI

```bash
make build
# ou manualmente:
go build -C tools/ctl -o ../../ctl .
```

### 2. Execute o setup interativo

```bash
./ctl setup
```

O CLI irá:
- Gerar CA própria + certificado wildcard `*.local.dev`
- Criar o arquivo `.env` com segredos aleatórios
- Criar a rede Docker `proxy`
- Fazer backup de arquivos existentes (opcional)

Para CI/CD, use o modo não-interativo:

```bash
./ctl setup --domain example.com --env prod --no-interactive
```

### 3. Configure o Keycloak

Aguarde o Keycloak ficar healthy (± 60s):

```bash
./ctl logs keycloak
# Aguarde: "Keycloak 26.6.x started"
```

O realm é importado automaticamente do template. O compose usa `envsubst` para
substituir variáveis do `.env` no `realm-template.json`.

### 4. Suba o stack completo

```bash
./ctl up
./ctl status   # verifique que todos estão healthy
```

---

## Comandos do CLI

| Comando | Descrição |
|---------|-----------|
| `./ctl setup` | Setup interativo do ambiente |
| `./ctl up` | Inicia todos os serviços |
| `./ctl down` | Para todos os serviços |
| `./ctl logs` | Logs do stack |
| `./ctl status` | Status dos serviços |
| `./ctl clean` | Remove containers (e opcionalmente volumes/certificados) |

---

## Estrutura de Arquivos

```
saas/
├── Makefile                        # Build targets
├── ctl                             # CLI compilado (Go)
│
├── infra/
│   ├── docker-compose.yml          # Orquestração principal
│   ├── .env                        # Segredos (não commitar)
│   ├── traefik/
│   │   ├── traefik.yml             # Config estática
│   │   ├── certs/                  # Certificados TLS
│   │   └── config/
│   │       └── middlewares.yml     # Config dinâmica
│   ├── keycloak/
│   │   └── realm-template.json     # Template do realm OIDC
│   └── oauth2-proxy/
│       └── oauth2-proxy.cfg.tmpl   # Config template
│
├── backend/                        # Python / FastAPI
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── src/
│       ├── main.py                 # App FastAPI + middlewares
│       ├── middleware/             # JWT auth + tenant RLS
│       └── infrastructure/
│           └── database/           # Models ORM, session
│
├── frontend/                       # React 19 / Vite / TypeScript
│   ├── Dockerfile                  # Multi-stage (nginx)
│   └── src/
│       └── App.tsx
│
└── tools/ctl/                      # Go CLI (Cobra + Bubbletea)
    ├── main.go
    ├── cmd/                        # Comandos: setup, up, down, etc.
    └── internal/                   # Cert, env, secrets, backup, tui
```

---

## Domínios e Serviços

| Domínio | Serviço | Middleware | Descrição |
|---|---|---|---|
| `traefik.local.dev` | Dashboard Traefik | BasicAuth | Monitoramento do proxy |
| `auth.local.dev` | Keycloak | security-headers | IdP / SSO |
| `app.local.dev` | Frontend + Backend | oauth2-auth + security-headers | App SaaS protegida |
| `api.local.dev` | (reservado) | security-headers + rate-limit | API interna |

---

## Segurança

### O que está implementado

- ✅ TLS obrigatório (HTTP → HTTPS redirect automático)
- ✅ Certificados auto-assinados via CA própria
- ✅ Headers de segurança OWASP (HSTS, CSP, X-Frame-Options, etc.)
- ✅ Rede Docker `internal` isolada (bancos não acessíveis externamente)
- ✅ Docker socket montado como **read-only**
- ✅ `exposedByDefault: false` no Traefik (princípio do menor privilégio)
- ✅ Segredos injetados via variáveis de ambiente (não hard-coded)
- ✅ Rate limiting nas rotas de API
- ✅ Brute-force protection no Keycloak
- ✅ Cookies HttpOnly + Secure + SameSite=Lax
- ✅ Headers sensíveis removidos dos logs de acesso
- ✅ Validação JWT com JWKS do Keycloak
- ✅ Isolamento multi-tenant via RLS do PostgreSQL

### Para produção, adicione

- [ ] Let's Encrypt (já configurado no Traefik, ativar com `TLS_RESOLVER=letsencrypt`)
- [ ] `ssl_insecure_skip_verify = false` no oauth2-proxy.cfg
- [ ] Keycloak com `KC_HOSTNAME_STRICT: "true"`
- [ ] Secrets gerenciados por Vault ou Docker Secrets
- [ ] MFA obrigatório no Keycloak
- [ ] Restrição de `email_domains` no oauth2-proxy
- [ ] Backup automático do volume `keycloak_db_data`
- [ ] Alertas de falha de login no Keycloak

---

## Troubleshooting

**`ERR_CERT_AUTHORITY_INVALID` no browser**
```bash
sudo cp infra/traefik/certs/rootCA.pem /usr/local/share/ca-certificates/ && sudo update-ca-certificates
# Reinicie o browser completamente após isso
```

**OAuth2-Proxy retorna `500 Internal Server Error`**
```bash
./ctl logs oauth2-proxy
# Verifique: OAUTH2_PROXY_CLIENT_SECRET correto? Keycloak healthy?
```

**Keycloak não inicia (erro de DB)**
```bash
./ctl logs keycloak-db
./ctl up
```

**ForwardAuth retorna 401 inesperado**
```bash
# Verifique se o cookie_domain está correto
# Cookie deve cobrir: .local.dev (com ponto inicial)
./ctl logs oauth2-proxy | grep -i "error\|invalid\|failed"
```

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
# Backend
cd backend && pytest -v

# CLI
cd tools/ctl && go test ./... -v

# Frontend
cd frontend && npm test
```
