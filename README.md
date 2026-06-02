# SaaS Local — Guia de Configuração
## Stack: Traefik v3.7 · Keycloak v26.6 · OAuth2-Proxy v7.15

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
# macOS
brew install mkcert docker

# Ubuntu/Debian
sudo apt install libnss3-tools
curl -fsSL https://github.com/FiloSottile/mkcert/releases/latest/download/mkcert-v*-linux-amd64 \
  -o /usr/local/bin/mkcert && chmod +x /usr/local/bin/mkcert
```

---

## Setup Inicial

### 1. Clone e configure o ambiente

```bash
git clone <seu-repo> saas-local && cd saas-local

# Copie e edite o .env (obrigatório antes de subir)
cp .env.example .env
nano .env
```

### 2. Execute o script de setup

```bash
chmod +x setup.sh
./setup.sh
```

O script irá:
- Instalar a CA do mkcert no sistema
- Gerar certificado wildcard `*.local.dev`
- Adicionar entradas no `/etc/hosts`
- Gerar o `OAUTH2_PROXY_COOKIE_SECRET` automaticamente
- Criar a rede Docker `proxy`
- Subir Traefik, Keycloak DB e Keycloak

### 3. Configurar o Keycloak

Aguarde o Keycloak ficar healthy (± 60s):

```bash
docker compose logs -f keycloak
# Aguarde: "Keycloak 26.6.x started"
```

**Opção A — Importar realm via CLI (recomendado):**

```bash
docker compose exec keycloak \
  /opt/keycloak/bin/kc.sh import \
  --file /opt/keycloak/data/import/realm-saas-local.json

# Para que o Keycloak leia o arquivo, monte o volume no compose:
# volumes:
#   - ./keycloak/realm-saas-local.json:/opt/keycloak/data/import/realm-saas-local.json:ro
```

Esse export já inclui o client `oauth2-proxy`, o mapper de `groups` e o audience mapper que faz o JWT trazer `aud=oauth2-proxy`.

**Opção B — Admin Console (manual):**

1. Acesse `https://auth.local.dev/admin`
2. Login com as credenciais do `.env`
3. Crie o realm `saas-local`
4. Crie o client `oauth2-proxy`:
   - Client type: **OpenID Connect**
   - Client authentication: **ON** (confidential)
   - Authentication flow: **Standard flow only**
   - Valid redirect URIs: `https://app.local.dev/oauth2/callback`
   - Web origins: `https://app.local.dev`
5. Em **Client scopes** do client, adicione um mapper **Audience** com `Included Client Audience = oauth2-proxy` e ative **Add to ID token** e **Add to access token**
6. Em **Mappers** ou **Client scopes**, mantenha o mapper de **Group Membership** com claim `groups` e `Full group path` ligado
7. Em **Credentials**, copie o **Client Secret**
8. Cole no `.env`: `OAUTH2_PROXY_CLIENT_SECRET=<secret>`

### 4. Suba o stack completo

```bash
docker compose up -d
docker compose ps   # verifique que todos estão healthy
```

---

## Estrutura de Arquivos

```
saas-local/
├── docker-compose.yml              # Orquestração principal
├── .env                            # Segredos (não commitar)
├── setup.sh                        # Bootstrap do ambiente
│
├── traefik/
│   ├── traefik.yml                 # Config estática (entrypoints, providers, TLS)
│   ├── certs/
│   │   ├── local.dev.crt           # Cert wildcard (gerado pelo mkcert)
│   │   └── local.dev.key
│   └── config/
│       └── middlewares.yml         # Config dinâmica (middlewares reutilizáveis)
│
├── keycloak/
│   └── realm-saas-local.json       # Export do realm para importação
│
└── oauth2-proxy/
    └── oauth2-proxy.cfg            # Config do OAuth2-Proxy
```

---

## Domínios e Serviços

| Domínio | Serviço | Middleware | Descrição |
|---|---|---|---|
| `traefik.local.dev` | Dashboard Traefik | BasicAuth | Monitoramento do proxy |
| `auth.local.dev` | Keycloak | security-headers | IdP / SSO |
| `app.local.dev` | App 1 | oauth2-auth + security-headers | App SaaS protegida |
| `api.local.dev` | App 2 | security-headers + rate-limit | API interna |

---

## Comandos Úteis

```bash
# Logs em tempo real
docker compose logs -f traefik
docker compose logs -f keycloak
docker compose logs -f oauth2-proxy

# Inspecionar certificado
openssl s_client -connect app.local.dev:443 -servername app.local.dev </dev/null 2>/dev/null \
  | openssl x509 -noout -dates

# Testar ForwardAuth manualmente
curl -v -k https://app.local.dev \
  -H "Cookie: _oauth2_proxy=<cookie_value>"

# Verificar OIDC Discovery do Keycloak
curl -sk https://auth.local.dev/realms/saas-local/.well-known/openid-configuration | jq .

# Gerar novo cookie secret
openssl rand -base64 32

# Exportar realm atual do Keycloak
docker compose exec keycloak \
  /opt/keycloak/bin/kc.sh export \
  --realm saas-local \
  --file /tmp/realm-export.json
docker compose cp keycloak:/tmp/realm-export.json ./keycloak/realm-saas-local.json

# Reiniciar apenas o oauth2-proxy (após mudar .env)
docker compose up -d --force-recreate oauth2-proxy
```

---

## Segurança

### O que está implementado

- ✅ TLS obrigatório (HTTP → HTTPS redirect automático)
- ✅ Certificados válidos localmente via mkcert
- ✅ Headers de segurança OWASP (HSTS, CSP, X-Frame-Options, etc.)
- ✅ Rede Docker `internal` isolada (Keycloak DB não acessível externamente)
- ✅ Docker socket montado como **read-only**
- ✅ `exposedByDefault: false` no Traefik (princípio do menor privilégio)
- ✅ Segredos injetados via variáveis de ambiente (não hard-coded)
- ✅ Rate limiting nas rotas de API
- ✅ Brute-force protection no Keycloak
- ✅ Cookies HttpOnly + Secure + SameSite=Lax
- ✅ Headers sensíveis removidos dos logs de acesso

### Para produção, adicione

- [ ] Certificados Let's Encrypt (substitua a seção `tls` do `traefik.yml`)
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
mkcert -install   # reinstala a CA no sistema
# Reinicie o browser completamente após isso
```

**OAuth2-Proxy retorna `500 Internal Server Error`**
```bash
docker compose logs oauth2-proxy
# Verifique: OAUTH2_PROXY_CLIENT_SECRET correto? Keycloak healthy?
```

**Keycloak não inicia (erro de DB)**
```bash
docker compose logs keycloak-db
docker compose restart keycloak-db
docker compose up -d keycloak
```

**ForwardAuth retorna 401 inesperado**
```bash
# Verifique se o cookie_domain está correto
# Cookie deve cobrir: .local.dev (com ponto inicial)
docker compose logs oauth2-proxy | grep -i "error\|invalid\|failed"
```
