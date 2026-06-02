#!/usr/bin/env bash
# =============================================================================
# setup.sh — Bootstraps o ambiente local
# Pré-requisitos: mkcert, docker, docker compose
# =============================================================================
set -euo pipefail

CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

log()  { echo -e "${CYAN}[SETUP]${NC} $*"; }
ok()   { echo -e "${GREEN}[OK]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
err()  { echo -e "${RED}[ERR]${NC} $*"; exit 1; }

# ---------------------------------------------------------------------------
# 1. Verifica dependências
# ---------------------------------------------------------------------------
log "Verificando dependências..."
for cmd in docker mkcert openssl; do
  command -v "$cmd" &>/dev/null || err "Comando '$cmd' não encontrado. Instale e tente novamente."
done
ok "Dependências OK"

# ---------------------------------------------------------------------------
# 2. Certificados TLS locais com mkcert
# ---------------------------------------------------------------------------
log "Instalando CA do mkcert no sistema..."
mkcert -install

log "Gerando certificado wildcard para *.local.dev..."
mkdir -p traefik/certs
mkcert -cert-file traefik/certs/local.dev.crt \
       -key-file  traefik/certs/local.dev.key \
       "local.dev" "*.local.dev"
ok "Certificados gerados em traefik/certs/"

# ---------------------------------------------------------------------------
# 3. Entradas no /etc/hosts
# ---------------------------------------------------------------------------
log "Configurando /etc/hosts..."
HOSTS=(
  "traefik.local.dev"
  "auth.local.dev"
  "app.local.dev"
  "api.local.dev"
)
for host in "${HOSTS[@]}"; do
  if grep -q "$host" /etc/hosts 2>/dev/null; then
    warn "$host já existe no /etc/hosts, pulando."
  else
    echo "127.0.0.1  $host" | sudo tee -a /etc/hosts > /dev/null
    ok "Adicionado: $host"
  fi
done

# ---------------------------------------------------------------------------
# 4. Gera Cookie Secret para o OAuth2-Proxy (se não existir no .env)
# ---------------------------------------------------------------------------
if [ -f .env ] && grep -q "COLE_O_VALOR_GERADO_PELO_OPENSSL_AQUI" .env; then
  log "Gerando OAUTH2_PROXY_COOKIE_SECRET..."
  COOKIE_SECRET=$(openssl rand -base64 32 | tr '+/' '-_')
  sed -i.bak "s|COLE_O_VALOR_GERADO_PELO_OPENSSL_AQUI|${COOKIE_SECRET}|" .env
  rm -f .env.bak
  ok "OAUTH2_PROXY_COOKIE_SECRET gerado e salvo no .env"
else
  warn "Pule geração do cookie — .env não encontrado ou já configurado."
fi

# ---------------------------------------------------------------------------
# 5. Cria a rede Docker (se necessário)
# ---------------------------------------------------------------------------
log "Criando rede Docker 'proxy'..."
docker network inspect proxy &>/dev/null || docker network create proxy
ok "Rede 'proxy' pronta"

# ---------------------------------------------------------------------------
# 6. Sobe o stack
# ---------------------------------------------------------------------------
echo ""
log "Iniciando o stack..."
docker compose up -d traefik keycloak-db keycloak

echo ""
ok "Stack iniciado! Próximos passos:"
echo ""
echo "  1. Aguarde o Keycloak ficar healthy:"
echo "     docker compose logs -f keycloak"
echo ""
echo "  2. Acesse o Admin Console do Keycloak:"
echo "     https://auth.local.dev/admin"
echo ""
echo "  3. Importe o realm 'saas-local' com o client 'oauth2-proxy'"
echo "     e confirme os mappers de groups e audience"
echo ""
echo "  4. Preencha o .env com KC_ADMIN_PASSWORD e OAUTH2_PROXY_CLIENT_SECRET"
echo ""
echo "  5. Suba o stack completo:"
echo "     docker compose up -d"
