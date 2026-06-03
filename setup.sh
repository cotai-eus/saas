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

ENV_FILE="infra/.env"

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
mkdir -p infra/traefik/certs
mkcert -cert-file infra/traefik/certs/local.dev.crt \
       -key-file  infra/traefik/certs/local.dev.key \
       "local.dev" "*.local.dev"
ok "Certificados gerados em infra/traefik/certs/"

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
# 4. Gera Secrets para o Stack (se não existir no .env)
# ---------------------------------------------------------------------------
if [ ! -f "$ENV_FILE" ]; then
  log "Criando $ENV_FILE a partir de placeholders..."
  cat <<EOF > "$ENV_FILE"
# Keycloak DB
KC_DB_NAME=keycloak
KC_DB_USER=keycloak
KC_DB_PASSWORD=TROQUE_ESTA_SENHA_FORTE_DB

# App DB
DB_NAME=saas
DB_USER=saas
DB_PASSWORD=TROQUE_ESTA_SENHA_FORTE_APP_DB
DB_HOST=app-db
DB_PORT=5432

# Keycloak Admin
KC_ADMIN_USER=admin
KC_ADMIN_PASSWORD=TROQUE_ESTA_SENHA_FORTE_ADMIN

# OAuth2-Proxy
OAUTH2_PROXY_CLIENT_SECRET=COLE_O_VALOR_GERADO_PELO_OPENSSL_AQUI_1
SAAS_API_CLIENT_SECRET=COLE_O_VALOR_GERADO_PELO_OPENSSL_AQUI_2
OAUTH2_PROXY_COOKIE_SECRET=COLE_O_VALOR_GERADO_PELO_OPENSSL_AQUI_3

# Traefik
TRAEFIK_DASHBOARD_PASSWORD_HASH=\$\$2y\$\$05\$\$Vv9Ct7OiPqanfr0J5T3fEO3.0JpIK3kEOkjXAG9VECMuHGNDrUSDC
EOF
fi

log "Configurando segredos em $ENV_FILE..."

# Cookie Secret
if grep -q "COLE_O_VALOR_GERADO_PELO_OPENSSL_AQUI_3" "$ENV_FILE"; then
  COOKIE_SECRET=$(openssl rand -base64 32 | tr '+/' '-_')
  sed -i "s|COLE_O_VALOR_GERADO_PELO_OPENSSL_AQUI_3|${COOKIE_SECRET}|" "$ENV_FILE"
  ok "OAUTH2_PROXY_COOKIE_SECRET gerado"
fi

# Client Secrets
if grep -q "COLE_O_VALOR_GERADO_PELO_OPENSSL_AQUI_1" "$ENV_FILE"; then
  SECRET1=$(openssl rand -base64 32)
  sed -i "s|COLE_O_VALOR_GERADO_PELO_OPENSSL_AQUI_1|${SECRET1}|" "$ENV_FILE"
  ok "OAUTH2_PROXY_CLIENT_SECRET gerado"
fi

if grep -q "COLE_O_VALOR_GERADO_PELO_OPENSSL_AQUI_2" "$ENV_FILE"; then
  SECRET2=$(openssl rand -base64 32)
  sed -i "s|COLE_O_VALOR_GERADO_PELO_OPENSSL_AQUI_2|${SECRET2}|" "$ENV_FILE"
  ok "SAAS_API_CLIENT_SECRET gerado"
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
# Nota: docker compose em infra/ detectará o .env automaticamente
cd infra && docker compose up -d traefik keycloak-db keycloak app-db && cd ..

echo ""
ok "Stack iniciado! Próximos passos:"
echo ""
echo "  1. Verifique os logs (do diretório infra/):"
echo "     docker compose logs -f keycloak"
echo ""
echo "  2. Acesse o Admin Console do Keycloak:"
echo "     https://auth.local.dev/admin"
echo ""
echo "  3. Verifique se o realm 'saas-local' foi importado corretamente."
echo ""
echo "  4. Configure o infra/.env com as senhas desejadas."
echo ""
echo "  5. Suba o stack completo (do diretório infra/):"
echo "     docker compose up -d"
