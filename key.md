I'll analyze this SaaS repository comprehensively as a Senior Software Architect. Let me start by examining the repository structure and codebase.Let me fetch the key files to understand the repository structure:Now let me check for the traefik and oauth2-proxy configurations:---

# 🔍 ANÁLISE ESTRATÉGICA PROFUNDA — SaaS Repository (cotai-eus/saas)

## **Resumo Executivo**

**Nota Geral da Arquitetura: 5.5/10**

Este é um **prototipo de infraestrutura de desenvolvimento com fundações sólidas, mas com limitações críticas para produção**. O repositório demonstra compreensão correta dos padrões OAuth2/OIDC e security best practices, mas é **puramente uma stack de autenticação/infra** — não há backend ou frontend implementados. A análise aponta vulnerabilidades, anti-patterns e um roadmap claro para evolução enterprise.

---

## **1. ARQUITETURA GERAL**

### 📊 Avaliação por Dimensão

| Dimensão | Score | Observação |
|----------|-------|-----------|
| **Organização do monorepo** | 4/10 | Apenas folders de infra (traefik, keycloak, oauth2-proxy). Sem backend Python, React, testes, CI/CD |
| **Separação de responsabilidades** | 7/10 | Traefik, Keycloak e OAuth2-Proxy bem isolados. Sem lógica de negócio para avaliar |
| **Acoplamento** | 6/10 | OAuth2-Proxy tightly coupled a Keycloak via hard-coded URLs e claims |
| **Coesão** | 6/10 | Middlewares bem definidos, mas faltam patterns para aplicações |
| **Clean Architecture** | N/A | Não há camadas de aplicação implementadas |
| **DDD** | N/A | Sem lógica de domínio definida |
| **Escalabilidade** | 4/10 | Docker Compose local; sem Kubernetes, without load balancing, single Keycloak instance |
| **Manutenibilidade** | 7/10 | Bom uso de Docker volumes, env vars. Documentação adequada |
| **Testabilidade** | 3/10 | Zero testes automatizados. Setup.sh é manual |

### 🎯 Problemas Críticos Identificados

#### **1.1 Falta de Backend e Frontend**
```
CRÍTICO: O repositório é apenas INFRAESTRUTURA de autenticação.
- Zero código Python (FastAPI, aplicação SaaS)
- Zero código React (frontend)
- Zero banco de dados de negócio
- Consequência: Impossível avaliar lógica, patterns, arquitetura real
```

#### **1.2 Monorepo Mal Estruturado**
```
saas/
├── docker-compose.yml          ✅ Bem estruturado
├── setup.sh                    ✅ Bom script de bootstrap
├── traefik/                    ✅ Organizado
├── keycloak/                   ✅ Config import
├── oauth2-proxy/               ✅ Config clara
└── [FALTAM: apps/, backend/, frontend/, tests/, .github/, docs/]
```

**Recomendação:**
```
saas/
├── infra/
│   ├── docker-compose.yml
│   ├── traefik/
│   ├── keycloak/
│   └── oauth2-proxy/
├── backend/
│   ├── src/
│   │   ├── domain/
│   │   ├── application/
│   │   ├── infrastructure/
│   │   ├── api/
│   │   └── __main__.py
│   ├── tests/
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/
│   ├── src/
│   ├── public/
│   ├── tests/
│   ├── package.json
│   └── Dockerfile
├── .github/
│   ├── workflows/
│   │   ├── ci.yml
│   │   ├── cd.yml
│   │   └── security.yml
├── docs/
│   ├── architecture.md
│   ├── auth-flow.md
│   └── deployment.md
├── docker-compose.local.yml
├── docker-compose.prod.yml
└── Makefile
```

#### **1.3 Sem Testes Automatizados**
```
CRÍTICO: Não há CI/CD, testes unitários ou integração
- Setup.sh é um script manual (frágil)
- Nenhuma verificação de sanidade
- Keycloak config exportada manualmente (prone to errors)
```

#### **1.4 Configuração Hardcoded em Vários Lugares**
```
❌ Problemas:
- traefik/traefik.yml: "traefik:8080" é fixo
- oauth2-proxy.cfg: redirect_url = "https://app.local.dev/..." (hardcoded)
- keycloak/realm-saas-local.json: client secret = "saas-local-oauth2-proxy-secret"
- keycloak: K_HOSTNAME_STRICT = "false" (development mode)

✅ Solução: Usar env vars e templates
```

---

## **2. SEGURANÇA**

### 🔐 Análise Completa

#### **2.1 Pontos Fortes**

✅ **OAuth2/OIDC Implementation:**
- Correto uso de Authorization Code Flow (standard flow)
- Client credentials confidential (client-secret obrigatório)
- Audience mapper garante que JWT é destinado ao oauth2-proxy
- PKCE (code_challenge_method = S256) habilitado

✅ **TLS:**
- HTTPS obrigatório (HTTP 301 para HTTPS)
- Certificados válidos via mkcert (local dev)
- Traefik com TLS termination

✅ **Cookies:**
- HttpOnly (previne XSS)
- Secure (HTTPS-only)
- SameSite=Lax (proteção contra CSRF)
- Cookie refresh (1h) + expiry (24h) razoável

✅ **Headers de Segurança:**
- HSTS (31536000s = 1 ano, incluindo subdomínios)
- X-Frame-Options: DENY (clickjacking)
- X-Content-Type-Options: nosniff (MIME sniffing)
- CSP básico implementado
- Referrer Policy: strict-origin-when-cross-origin
- Permissions Policy restringe features

✅ **Rede Isolada:**
- Docker `internal` network sem acesso a internet
- Keycloak DB não exposto externamente
- Docker socket montado como read-only

✅ **Princípio do Menor Privilégio:**
- `exposedByDefault: false` no Traefik (apenas containers com label habilitados)
- ForwardAuth no Traefik (não proxy completo)

✅ **Brute Force Protection:**
- Keycloak: `bruteForceProtected: true`
- `failureFactor: 5`, `maxFailureWaitSeconds: 900`

---

#### **2.2 Vulnerabilidades e Riscos**

| ID | Categoria | Severidade | Descrição | Impacto | Solução |
|-----|-----------|------------|-----------|---------|---------|
| **SEC-001** | OIDC Config | **CRÍTICA** | `KC_HOSTNAME_STRICT = "false"` em docker-compose | IdP pode ser enganado via Host header injection | Alterar para `"true"` e usar `KC_HOSTNAME=auth.prod.dev` |
| **SEC-002** | OAuth2-Proxy | **CRÍTICA** | `ssl_insecure_skip_verify = true` permanente | MITM attack contra Keycloak | Remover flag em produção; usar CA properly |
| **SEC-003** | Keycloak | **ALTA** | Client secret hard-coded no realm JSON: `"saas-local-oauth2-proxy-secret"` | Se JSON vazar, secret compromised | Usar Vault/sealed-secrets; gerar via script |
| **SEC-004** | Password | **ALTA** | Senha temporária do test-user no realm: `"Test@12345678"` | Test credentials em produção? | Remover do JSON; usar LDAP/SSO federation |
| **SEC-005** | Token Lifetime | **MÉDIA** | Access token lifetime = 300s (5 min) → bom | Refresh token não tem limite explícito | Adicionar `offlineSessionMaxLifespan` |
| **SEC-006** | Keycloak | **MÉDIA** | Password policy obrigatória (12+ chars, special) | Positivo, mas muito rigorosa para dev | Ramificar policy: DEV (simples) vs PROD (estrita) |
| **SEC-007** | OAuth2-Proxy | **MÉDIA** | `email_domains = ["*"]` permite qualquer domínio | Aberto demais para SaaS multi-tenant | Usar `email_domains = ["suaempresa.com"]` ou valida por tenant |
| **SEC-008** | RBAC | **MÉDIA** | Grupos hardcoded: `allowed_groups = ["/app-users"]` | Não há suporte para ABAC ou tenant-based access | Adicionar claim `tenant_id` customizado |
| **SEC-009** | CORS | **ALTA** | CSP content-security-policy comentado: `fra[...]` | CSP está truncado/incompleto | Completar CSP; testar com helmet.js (React) |
| **SEC-010** | Rate Limit | **MÉDIA** | Rate limit 100 req/min é muito alto | DDoS/brute force ainda viável | Reduzir para 20 req/min para APIs sensíveis |
| **SEC-011** | Session | **MÉDIA** | `revokeRefreshToken = true` | Bom (força reauth). Mas sem logout endpoint cleanup | Implementar logout hook no Keycloak |
| **SEC-012** | Audit | **ALTA** | Zero audit logs implementado | Compliance impossível | Habilitar KC_METRICS_ENABLED, event listeners |
| **SEC-013** | MFA | **CRÍTICA** | MFA não mencionado | Apenas password factor | Configurar OTP/WebAuthn no Keycloak realm |
| **SEC-014** | Admin | **CRÍTICA** | BasicAuth dashboard: `admin:$$2y$$05$$Vv9Ct7O...` (changeme) | Senha padrão hardcoded | Usar OAuth2-Proxy para proteger traefik |
| **SEC-015** | PKCE | **MÉDIA** | PKCE habilitado mas `skip_jwt_bearer_tokens` comentado | Sem validação de Bearer tokens para APIs | Implementar JWT validation upstream |

---

#### **2.3 Vulnerabilidades por Tipo**

**OWASP Top 10:**

| Vulnerabilidade | Status | Mitigação |
|---|---|---|
| **A01 Broken Access Control** | ⚠️ PARCIAL | RBAC simples; sem ABAC. Multi-tenancy não definida |
| **A02 Cryptographic Failures** | ✅ BOM | TLS obrigatório, cookies secure |
| **A03 Injection** | N/A | Sem aplicação web |
| **A04 Insecure Design** | ⚠️ MÉDIO | Password policy OK; MFA missing |
| **A05 Security Misconfiguration** | ⚠️ CRÍTICO | `KC_HOSTNAME_STRICT=false`, secrets em JSON |
| **A06 Vulnerable Components** | ✅ BOM | Todas imagens com SHA256, atualizadas |
| **A07 Auth & Session Mgmt** | ✅ MUITO BOM | OAuth2/OIDC correto; cookie handling OK |
| **A08 Software & Data Integrity** | ⚠️ MÉDIO | Sem verificação de assinatura de imagens |
| **A09 Logging & Monitoring** | ❌ NÃO | Métricas comentadas; sem observabilidade |
| **A10 SSRF** | ⚠️ MÉDIO | `oauth2-proxy` pode ser explorado se misconfigured |

---

#### **2.4 Multi-Tenancy & Data Segregation**

```
❌ CRÍTICO: Zero implementação de multi-tenancy

Problemas:
1. Keycloak realm é único: "saas-local"
   → Todos os usuários no mesmo realm
   → Sem isolamento de dados por tenant
   
2. Grupos e Roles não mapeiam a tenant:
   allowed_groups = ["/app-users"]  # não tem tenant_id
   
3. OAuth2-Proxy injeta headers genéricos:
   X-Auth-Request-User        # não tem tenant context
   X-Auth-Request-Groups      # não tem tenant context
   
4. Banco de dados: não há schema de isolação mencionado

Solução Recomendada:
1. Multi-realm approach:
   - Cada tenant = um realm no Keycloak
   - realm-acme.com, realm-customer.dev
   
   OU
   
2. Single realm + custom claims:
   - Adicionar mapper customizado: "tenant_id" → JWT claim
   - OAuth2-Proxy injeta: X-Tenant-ID header
   - Backend valida tenant_id em contexto de request
   
3. Database isolation:
   - Row-level security (RLS) no PostgreSQL
   - Schema per tenant (problemas de scaling)
   - Dedicated database per tenant (muito caro)
```

---

### 🎯 Classificação de Vulnerabilidades por Criticidade

#### **CRÍTICAS (5):**
1. `KC_HOSTNAME_STRICT=false` → Host header injection
2. `ssl_insecure_skip_verify=true` permanente
3. Client secret hardcoded em JSON
4. Test user senha em produção (se aplica)
5. MFA não implementado

#### **ALTAS (5):**
1. `email_domains = ["*"]` 
2. CSP incompleto/truncado
3. Sem audit logging
4. Admin BasicAuth com senha padrão
5. Sem logout event cleanup

#### **MÉDIAS (5):**
1. Access token lifetime curto (mas OK)
2. Rate limit alto (100/min)
3. Grupos sem tenant context
4. Sem JWT validation para APIs
5. `allowed_roles = ["user"]` muito genérico

---

## **3. BACKEND PYTHON**

### Status: **NÃO IMPLEMENTADO**

```
⚠️  CRÍTICO: Não há código Python no repositório.

Assumptions for evaluation:
- Stack esperado: FastAPI (moderno) ou Flask/Django (enterprise)
- Database: PostgreSQL 14+
- Cache: Redis
- Async: asyncio + aiohttp
- Job queue: Celery ou Temporal
```

### 📋 Arquitetura Recomendada

```
backend/
├── src/
│   ├── __init__.py
│   ├── main.py                          # FastAPI app
│   ├── config.py                        # Settings (Pydantic v2)
│   ├── dependencies.py                  # DI container
│   │
│   ├── domain/                          # Business logic
│   │   ├── __init__.py
│   │   ├── models/                      # Entity definitions
│   │   │   ├── tenant.py
│   │   │   ├── user.py
│   │   │   ├── subscription.py
│   │   │   └── audit.py
│   │   ├── events/                      # Domain events
│   │   │   ├── tenant_created.py
│   │   │   ├── user_invited.py
│   │   │   └── subscription_updated.py
│   │   ├── exceptions/                  # Domain exceptions
│   │   │   ├── tenant_not_found.py
│   │   │   ├── invalid_email.py
│   │   │   └── insufficient_permissions.py
│   │   └── value_objects/               # Value objects
│   │       ├── email.py
│   │       ├── tenant_id.py
│   │       └── subscription_plan.py
│   │
│   ├── application/                     # Use cases & services
│   │   ├── __init__.py
│   │   ├── dto/                         # Data Transfer Objects
│   │   │   ├── tenant_dto.py
│   │   │   ├── user_dto.py
│   │   │   └── subscription_dto.py
│   │   ├── services/                    # Business orchestration
│   │   │   ├── tenant_service.py
│   │   │   ├── user_service.py
│   │   │   ├── subscription_service.py
│   │   │   ├── email_service.py
│   │   │   └── audit_service.py
│   │   └── repositories/
│   │       ├── tenant_repository.py
│   │       ├── user_repository.py
│   │       └── subscription_repository.py
│   │
│   ├── infrastructure/                  # Technical implementations
│   │   ├── __init__.py
│   │   ├── persistence/
│   │   │   ├── __init__.py
│   │   │   ├── models.py                # SQLAlchemy ORM models
│   │   │   ├── session.py               # DB session management
│   │   │   ├── migrations/              # Alembic
│   │   │   │   ├── env.py
│   │   │   │   ├── script.py.mako
│   │   │   │   └── versions/
│   │   │   │       ├── 001_initial.py
│   │   │   │       └── ...
│   │   │   └── repositories/
│   │   │       ├── sqlalchemy_tenant_repo.py
│   │   │       ├── sqlalchemy_user_repo.py
│   │   │       └── sqlalchemy_subscription_repo.py
│   │   ├── cache/
│   │   │   ├── __init__.py
│   │   │   ├── redis_client.py
│   │   │   └── cache_service.py
│   │   ├── email/
│   │   │   ├── __init__.py
│   │   │   └── smtp_provider.py          # or SendGrid, Mailgun
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── oauth2_provider.py        # Keycloak integration
│   │   │   ├── jwt_handler.py
│   │   │   └── permissions.py            # Permission checking
│   │   ├── observability/
│   │   │   ├── __init__.py
│   │   │   ├── logger.py
│   │   │   ├── tracer.py                 # OpenTelemetry
│   │   │   ├── metrics.py                # Prometheus
│   │   │   └── instrumentation.py
│   │   └── jobs/
│   │       ├── __init__.py
│   │       ├── celery_app.py
│   │       └── tasks/
│   │           ├── send_email.py
│   │           ├── cleanup_sessions.py
│   │           └── generate_reports.py
│   │
│   ├── api/                             # HTTP layer
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── tenants.py           # Tenant endpoints
│   │   │   │   ├── users.py             # User endpoints
│   │   │   │   ├── subscriptions.py     # Subscription endpoints
│   │   │   │   ├── auth.py              # Auth endpoints
│   │   │   │   └── health.py            # Health check
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── auth_middleware.py       # JWT validation
│   │   │   ├── tenant_middleware.py     # Tenant context extraction
│   │   │   ├── correlation_id.py        # Request tracing
│   │   │   └── error_handler.py         # Global error handling
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── tenant_schema.py
│   │   │   ├── user_schema.py
│   │   │   ├── subscription_schema.py
│   │   │   └── error_schema.py
│   │   └── dependencies/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── db.py
│   │       └── tenant.py
│   │
│   └── shared/                          # Cross-cutting concerns
│       ├── __init__.py
│       ├── exceptions.py                # Global exceptions
│       ├── types.py                     # Type definitions
│       └── utils.py                     # Utilities
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                      # Pytest fixtures
│   ├── unit/
│   │   ├── domain/
│   │   ├── application/
│   │   └── infrastructure/
│   ├── integration/
│   │   ├── db/
│   │   ├── auth/
│   │   └── api/
│   └── e2e/
│       ├── auth_flow.py
│       ├── tenant_creation.py
│       └── subscription_upgrade.py
│
├── pyproject.toml                       # Poetry dependencies
├── poetry.lock
├── Dockerfile
├── .dockerignore
└── docker-compose.override.yml          # Dev settings
```

### 🎯 Implementação Recomendada

#### **Stack:**
```python
# FastAPI 0.104+
# SQLAlchemy 2.0+ (async support)
# Pydantic v2 (serialization)
# Alembic (migrations)
# Pytest + pytest-asyncio (testing)
# OpenTelemetry (tracing)
# Prometheus (metrics)
# structlog (logging)
# Celery + Redis (async jobs)
```

#### **Key Features:**

```python
# 1. Dependency Injection
from fastapi import Depends
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    
    # Database
    db = providers.Singleton(
        SessionLocal,
        url=config.database.url
    )
    
    # Repositories
    tenant_repo = providers.Factory(
        TenantRepository,
        session=db
    )
    
    # Services
    tenant_service = providers.Factory(
        TenantService,
        repo=tenant_repo
    )

# 2. Multi-Tenant Context
from contextvars import ContextVar

tenant_context: ContextVar[str] = ContextVar("tenant_id")

async def get_tenant_id(
    request: Request,
    token: str = Depends(oauth2_scheme)
) -> str:
    # Extract from X-Tenant-ID header or JWT claim
    tenant_id = request.headers.get("X-Tenant-ID")
    if not tenant_id:
        claims = decode_jwt(token)
        tenant_id = claims.get("tenant_id")
    
    token.set(tenant_id)
    return tenant_id

# 3. Error Handling
from fastapi.exception_handlers import RequestValidationError

class DomainError(Exception):
    """Base domain error"""
    pass

class TenantNotFound(DomainError):
    pass

@app.exception_handler(DomainError)
async def domain_exception_handler(request: Request, exc: DomainError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

# 4. Database Session Management
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine(
    "postgresql+asyncpg://...",
    echo=False,
    pool_size=20,
    max_overflow=10
)

async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

# 5. Migrations with Alembic
# alembic revision --autogenerate -m "Add tenant table"
# alembic upgrade head

# 6. Observability
from opentelemetry import trace, metrics
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

@app.middleware("http")
async def add_trace_id(request: Request, call_next):
    with tracer.start_as_current_span("http_request"):
        response = await call_next(request)
        return response

# 7. Async Jobs
from celery import Celery

app_celery = Celery(__name__)

@app_celery.task
async def send_welcome_email(user_id: str):
    # Async job execution
    pass
```

---

## **4. FRONTEND REACT**

### Status: **NÃO IMPLEMENTADO**

```
⚠️  CRÍTICO: Não há código React no repositório.

Assumptions:
- TypeScript (mandatory for production)
- TanStack Query (data fetching)
- TanStack Router (routing)
- State management: Zustand ou Redux Toolkit
- UI Kit: Material-UI, shadcn/ui, ou custom Design System
```

### 📋 Arquitetura Recomendada

```
frontend/
├── src/
│   ├── main.tsx                         # Vite entry point
│   ├── index.css
│   │
│   ├── app.tsx                          # Root component
│   │
│   ├── features/                        # Feature-based structure
│   │   ├── auth/
│   │   │   ├── components/
│   │   │   │   ├── LoginButton.tsx
│   │   │   │   ├── LogoutButton.tsx
│   │   │   │   ├── ProtectedRoute.tsx
│   │   │   │   └── AuthCheck.tsx
│   │   │   ├── hooks/
│   │   │   │   ├── useAuth.ts
│   │   │   │   ├── useOAuth2Callback.ts
│   │   │   │   └── useAuthToken.ts
│   │   │   ├── services/
│   │   │   │   └── authApi.ts
│   │   │   ├── stores/
│   │   │   │   └── authStore.ts         # Zustand
│   │   │   ├── types/
│   │   │   │   └── auth.ts
│   │   │   └── auth-layout.tsx
│   │   │
│   │   ├── tenants/
│   │   │   ├── components/
│   │   │   │   ├── TenantList.tsx
│   │   │   │   ├── TenantCard.tsx
│   │   │   │   ├── CreateTenantModal.tsx
│   │   │   │   └── TenantSettings.tsx
│   │   │   ├── hooks/
│   │   │   │   ├── useTenants.ts
│   │   │   │   ├── useCreateTenant.ts
│   │   │   │   └── useTenantSettings.ts
│   │   │   ├── services/
│   │   │   │   └── tenantApi.ts
│   │   │   ├── queries/
│   │   │   │   ├── tenantQueries.ts     # TanStack Query
│   │   │   │   └── tenantMutations.ts
│   │   │   ├── types/
│   │   │   │   └── tenant.ts
│   │   │   └── pages/
│   │   │       ├── TenantsPage.tsx
│   │   │       └── TenantDetailPage.tsx
│   │   │
│   │   ├── users/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── services/
│   │   │   ├── queries/
│   │   │   ├── types/
│   │   │   └── pages/
│   │   │
│   │   ├── subscriptions/
│   │   │   └── ...
│   │   │
│   │   └── dashboard/
│   │       ├── components/
│   │       │   ├── MetricsCard.tsx
│   │       │   ├── ChartWidget.tsx
│   │       │   └── ActivityFeed.tsx
│   │       ├── hooks/
│   │       ├── services/
│   │       └── pages/
│   │           └── DashboardPage.tsx
│   │
│   ├── shared/                          # Cross-feature utilities
│   │   ├── api/
│   │   │   ├── client.ts                # Axios/fetch instance
│   │   │   ├── interceptors.ts          # Auth token injection
│   │   │   └── errorHandler.ts          # Global error handling
│   │   │
│   │   ├── components/
│   │   │   ├── Layout/
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   ├── Footer.tsx
│   │   │   │   └── MainLayout.tsx
│   │   │   ├── ErrorBoundary.tsx
│   │   │   ├── Loading.tsx
│   │   │   ├── Modal.tsx
│   │   │   └── Toast.tsx
│   │   │
│   │   ├── hooks/
│   │   │   ├── useAsync.ts
│   │   │   ├── useLocalStorage.ts
│   │   │   ├── useDebounce.ts
│   │   │   ├── useFetch.ts
│   │   │   └── useTenant.ts              # Current tenant context
│   │   │
│   │   ├── stores/
│   │   │   ├── appStore.ts              # Global app state
│   │   │   └── notificationStore.ts
│   │   │
│   │   ├── theme/
│   │   │   ├── colors.ts
│   │   │   ├── typography.ts
│   │   │   ├── spacing.ts
│   │   │   └── useTheme.ts
│   │   │
│   │   ├── types/
│   │   │   ├── api.ts
│   │   │   ├── common.ts
│   │   │   └── errors.ts
│   │   │
│   │   └── utils/
│   │       ├── formatting.ts
│   │       ├── validation.ts
│   │       ├── date.ts
│   │       └── constants.ts
│   │
│   ├── routes/
│   │   ├── index.tsx                    # TanStack Router config
│   │   ├── root-route.tsx
│   │   ├── auth-routes.tsx
│   │   ├── app-routes.tsx
│   │   └── admin-routes.tsx
│   │
│   └── config/
│       ├── env.ts                       # Environment variables
│       ├── api-config.ts
│       └── auth-config.ts
│
├── tests/
│   ├── __mocks__/
│   ├── unit/
│   │   ├── utils/
│   │   ├── hooks/
│   │   └── stores/
│   ├── integration/
│   │   ├── features/
│   │   └── components/
│   └── e2e/
│       ├── auth.spec.ts
│       └── tenant-management.spec.ts
│
├── public/
│   ├── index.html
│   ├── favicon.ico
│   └── manifest.json
│
├── vite.config.ts
├── tsconfig.json
├── package.json
├── Dockerfile
├── docker-compose.override.yml
└── .env.example
```

### 🎯 Implementação Recomendada

#### **Stack:**
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@tanstack/react-query": "^5.28.0",
    "@tanstack/react-router": "^1.24.0",
    "zustand": "^4.4.0",
    "axios": "^1.6.0",
    "@mui/material": "^5.14.0",
    "zod": "^3.22.0",
    "typescript": "^5.3.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.2.0",
    "vitest": "^0.34.0",
    "@testing-library/react": "^14.1.0",
    "cypress": "^13.6.0"
  }
}
```

#### **Key Features:**

```typescript
// 1. OAuth2/OIDC Integration
import { useEffect } from 'react';
import { useNavigate, useSearch } from '@tanstack/react-router';
import { authStore } from '@/shared/stores/authStore';

export function OAuth2Callback() {
  const navigate = useNavigate();
  const { code } = useSearch({ from: '/auth/callback' });
  
  useEffect(() => {
    if (code) {
      // OAuth2-Proxy handles callback, we just wait for cookie
      const checkAuth = setInterval(() => {
        const hasAuth = document.cookie.includes('_oauth2_proxy');
        if (hasAuth) {
          clearInterval(checkAuth);
          authStore.setIsAuthenticated(true);
          navigate({ to: '/dashboard' });
        }
      }, 500);
      
      return () => clearInterval(checkAuth);
    }
  }, [code, navigate]);
  
  return <Loading>Authenticating...</Loading>;
}

// 2. TanStack Query Setup
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,     // 5 minutes
      gcTime: 10 * 60 * 1000,        // 10 minutes
      retry: 1,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 0,
    },
  },
});

// 3. Protected Route
import { Navigate } from '@tanstack/react-router';
import { authStore } from '@/shared/stores/authStore';

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = authStore();
  
  if (!isAuthenticated) {
    return <Navigate to="/auth/login" replace />;
  }
  
  return children;
}

// 4. Auth Hook
export function useAuth() {
  const { isAuthenticated, user } = authStore();
  
  const logout = async () => {
    // Redirect to /oauth2/sign_out (OAuth2-Proxy endpoint)
    window.location.href = '/oauth2/sign_out';
  };
  
  const checkSession = async () => {
    try {
      const response = await apiClient.get('/api/auth/me');
      authStore.setUser(response.data);
      authStore.setIsAuthenticated(true);
    } catch {
      authStore.setIsAuthenticated(false);
    }
  };
  
  return { isAuthenticated, user, logout, checkSession };
}

// 5. Tenant Context
import { create } from 'zustand';

interface TenantStore {
  currentTenant: Tenant | null;
  setCurrentTenant: (tenant: Tenant) => void;
}

export const useTenantStore = create<TenantStore>((set) => ({
  currentTenant: null,
  setCurrentTenant: (tenant) => set({ currentTenant: tenant }),
}));

// 6. API Client with Interceptor
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  withCredentials: true,  // Include cookies (OAuth2-Proxy)
});

// Inject tenant context header
apiClient.interceptors.request.use((config) => {
  const tenantId = useTenantStore.getState().currentTenant?.id;
  if (tenantId) {
    config.headers['X-Tenant-ID'] = tenantId;
  }
  return config;
});

// 7. Error Handling
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Session expired, redirect to login
      window.location.href = '/auth/login';
    }
    
    if (error.response?.status === 403) {
      // Insufficient permissions
      notificationStore.showError('You don\'t have permission for this action');
    }
    
    return Promise.reject(error);
  }
);

// 8. TanStack Query Integration
import { useQuery, useMutation } from '@tanstack/react-query';

export const tenantQueries = {
  all: () => ['tenants'],
  lists: () => [...tenantQueries.all(), 'list'],
  list: (page: number) => [...tenantQueries.lists(), page],
  details: () => [...tenantQueries.all(), 'detail'],
  detail: (id: string) => [...tenantQueries.details(), id],
};

export function useTenants(page: number) {
  return useQuery({
    queryKey: tenantQueries.list(page),
    queryFn: () => apiClient.get(`/api/tenants?page=${page}`),
  });
}

export function useUpdateTenant() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: TenantUpdate }) =>
      apiClient.patch(`/api/tenants/${id}`, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: tenantQueries.details(),
      });
    },
  });
}

// 9. Error Boundary
import { ErrorBoundary as ErrorBoundaryComponent } from 'react-error-boundary';

function ErrorFallback({ error, resetErrorBoundary }: any) {
  return (
    <div role="alert">
      <h2>Something went wrong</h2>
      <pre>{error.message}</pre>
      <button onClick={resetErrorBoundary}>Try again</button>
    </div>
  );
}

export function ErrorBoundary({ children }: { children: React.ReactNode }) {
  return (
    <ErrorBoundaryComponent FallbackComponent={ErrorFallback}>
      {children}
    </ErrorBoundaryComponent>
  );
}

// 10. TanStack Router Configuration
import { RootRoute, Route, Router } from '@tanstack/react-router';

const rootRoute = new RootRoute({
  component: () => (
    <div>
      <MainLayout />
      <Outlet />
    </div>
  ),
});

const dashboardRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/dashboard',
  component: () => <ProtectedRoute><DashboardPage /></ProtectedRoute>,
});

const tenantDetailRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/tenants/$tenantId',
  component: () => <TenantDetailPage />,
});

const routeTree = rootRoute.addChildren([
  dashboardRoute,
  tenantDetailRoute,
]);

const router = new Router({ routeTree });

export default router;
```

---

## **5. DEVOPS E INFRAESTRUTURA**

### 📊 Avaliação

| Aspecto | Score | Status |
|---------|-------|--------|
| **Docker** | 8/10 | ✅ BOM: Imagens com SHA256, sem root, readiness probes |
| **Docker Compose** | 7/10 | ✅ BOM: Bem estruturado, health checks, volumes nomeados |
| **Kubernetes Ready** | 2/10 | ❌ NÃO: Sem Helm charts, manifests K8s, resource limits |
| **GitOps** | 1/10 | ❌ NÃO: Sem ArgoCD, Flux, GitHub Actions |
| **CI/CD** | 0/10 | ❌ AUSENTE: Zero pipelines |
| **Secrets Management** | 3/10 | ⚠️ CRÍTICO: .env file, hardcoded secrets em JSON |
| **Observability** | 2/10 | ⚠️ MÍNIMO: Logs JSON, mas sem centralização |
| **OpenTelemetry** | 0/10 | ❌ NÃO IMPLEMENTADO |
| **Prometheus** | 0/10 | ❌ COMENTADO NO TRAEFIK |
| **Grafana** | 0/10 | ❌ NÃO IMPLEMENTADO |
| **Loki** | 0/10 | ❌ NÃO IMPLEMENTADO |
| **Tempo** | 0/10 | ❌ NÃO IMPLEMENTADO |

---

### 🔧 Problemas Críticos

#### **5.1 Docker Compose é Apenas Dev**

```yaml
❌ PROBLEMA:
docker-compose.yml define TUDO em um arquivo
- Traefik, Keycloak, OAuth2-Proxy, apps
- Sem separação DEV/PROD
- Sem namespaces de recurso

✅ SOLUÇÃO:
# docker-compose.local.yml — Development (current)
# docker-compose.prod.yml  — Production

# Prod deve incluir:
# - Resource limits (memory, CPU)
# - Restart policies (always)
# - Healthcheck timeouts maiores
# - Logging drivers centralizados
# - Secrets from Docker Secrets / Vault
# - Spread across multiple nodes
```

**Dockerfile Recomendado:**
```dockerfile
# --- Traefik ---
# Não precisa de Dockerfile (usar imagem oficial)
# Mas criar um init script para certificados Let's Encrypt

# --- Keycloak (otimizado para produção) ---
FROM quay.io/keycloak/keycloak:26.6 AS builder

ENV KC_HEALTH_ENABLED=true
ENV KC_METRICS_ENABLED=true
ENV KC_DB=postgres

WORKDIR /opt/keycloak
RUN /opt/keycloak/bin/kc.sh build

FROM quay.io/keycloak/keycloak:26.6

COPY --from=builder /opt/keycloak/lib/quarkus/ /opt/keycloak/lib/quarkus/
COPY --from=builder /opt/keycloak/lib/lib/ /opt/keycloak/lib/lib/

ENV KC_DB=postgres
ENV KC_HTTP_ENABLED=false
ENV KC_HTTP_PORT=8080
ENV KC_HTTPS_PORT=8443

EXPOSE 8443 9000

ENTRYPOINT ["/opt/keycloak/bin/kc.sh"]

# --- OAuth2-Proxy ---
# Usar imagem oficial quay.io/oauth2-proxy/oauth2-proxy

# --- Backend Python (FastAPI) ---
FROM python:3.12-slim AS builder

WORKDIR /app
COPY pyproject.toml poetry.lock* ./
RUN pip install poetry && poetry install --no-dev

FROM python:3.12-slim

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY src ./src

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

# --- Frontend React ---
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1
```

---

#### **5.2 Kubernetes Não Está Preparado**

```yaml
❌ PROBLEMA:
Sem suporte a K8s
- Sem resource requests/limits
- Sem liveness/readiness probes padrão K8s
- Sem service mesh (Istio)
- Sem ingress controllers

✅ SOLUÇÃO: Helm Chart para Production

# helm/
# ├── Chart.yaml
# ├── values.yaml              # default values
# ├── values-dev.yaml          # dev overrides
# ├── values-prod.yaml         # prod overrides
# ├── values-staging.yaml      # staging overrides
# ├── templates/
# │   ├── _helpers.tpl
# │   ├── traefik-deployment.yaml
# │   ├── traefik-service.yaml
# │   ├── keycloak-deployment.yaml
# │   ├── keycloak-service.yaml
# │   ├── keycloak-ingress.yaml
# │   ├── oauth2-proxy-deployment.yaml
# │   ├── oauth2-proxy-service.yaml
# │   ├── backend-deployment.yaml
# │   ├── backend-service.yaml
# │   ├── backend-hpa.yaml       # Horizontal Pod Autoscaler
# │   ├── frontend-deployment.yaml
# │   ├── frontend-service.yaml
# │   ├── configmap.yaml
# │   ├── secret.yaml
# │   ├── networkpolicy.yaml
# │   ├── pdb.yaml               # Pod Disruption Budget
# │   └── prometheus-servicemonitor.yaml
# └── kustomization.yaml

# values-prod.yaml example:
traefik:
  replicas: 3
  resources:
    requests:
      cpu: 250m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi
  affinity:
    podAntiAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchExpressions:
            - key: app
              operator: In
              values:
              - traefik
          topologyKey: kubernetes.io/hostname

keycloak:
  replicas: 3
  resources:
    requests:
      cpu: 500m
      memory: 1Gi
    limits:
      cpu: 1000m
      memory: 2Gi
  livenessProbe:
    httpGet:
      path: /health/live
      port: 9000
    initialDelaySeconds: 60
    periodSeconds: 10
  readinessProbe:
    httpGet:
      path: /health/ready
      port: 9000
    initialDelaySeconds: 40
    periodSeconds: 10

backend:
  replicas: 3
  resources:
    requests:
      cpu: 250m
      memory: 512Mi
    limits:
      cpu: 500m
      memory: 1Gi
  hpa:
    enabled: true
    minReplicas: 3
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70
    targetMemoryUtilizationPercentage: 80

frontend:
  replicas: 2
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 200m
      memory: 256Mi
```

**Exemplo de Deployment K8s:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: saas
  labels:
    app: backend
    version: v1
spec:
  replicas: 3
  
  selector:
    matchLabels:
      app: backend
  
  template:
    metadata:
      labels:
        app: backend
        version: v1
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
        prometheus.io/path: "/metrics"
    
    spec:
      serviceAccountName: backend
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - backend
              topologyKey: kubernetes.io/hostname
      
      containers:
      - name: backend
        image: gcr.io/saas-project/backend:latest
        imagePullPolicy: IfNotPresent
        
        ports:
        - name: http
          containerPort: 8000
          protocol: TCP
        - name: metrics
          containerPort: 8001
          protocol: TCP
        
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: LOG_LEVEL
          value: "INFO"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: backend-secrets
              key: database-url
        - name: KEYCLOAK_URL
          value: "https://auth.saas.com"
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: backend-secrets
              key: redis-url
        
        resources:
          requests:
            cpu: 250m
            memory: 512Mi
          limits:
            cpu: 500m
            memory: 1Gi
        
        livenessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        
        readinessProbe:
          httpGet:
            path: /health/ready
            port: http
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 5
          failureThreshold: 2
        
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
        
        volumeMounts:
        - name: tmp
          mountPath: /tmp
        - name: cache
          mountPath: /app/cache
      
      volumes:
      - name: tmp
        emptyDir: {}
      - name: cache
        emptyDir: {}
      
      terminationGracePeriodSeconds: 30

---
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: saas
spec:
  type: ClusterIP
  selector:
    app: backend
  ports:
  - name: http
    port: 8000
    targetPort: http
    protocol: TCP
  - name: metrics
    port: 8001
    targetPort: metrics
    protocol: TCP

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend
  namespace: saas
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

#### **5.3 GitOps Ausente**

```yaml
❌ PROBLEMA:
Sem GitOps (ArgoCD, Flux)
- Deploy é manual
- Sem rollback automático
- Sem auditoria de mudanças

✅ SOLUÇÃO: ArgoCD + Git como source of truth

# .github/workflows/deploy.yml
name: Deploy via ArgoCD

on:
  push:
    branches: [main, staging]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: ./backend
        push: true
        tags: |
          gcr.io/${{ secrets.GCP_PROJECT }}/backend:${{ github.sha }}
          gcr.io/${{ secrets.GCP_PROJECT }}/backend:latest
    
    - name: Update Helm values in GitOps repo
      run: |
        git clone https://github.com/cotai-eus/saas-gitops.git
        cd saas-gitops
        
        # Update image tag
        sed -i "s|backend:.*|backend:${{ github.sha }}|" environments/${{ github.ref_name }}/values.yaml
        
        git config user.name "CI Bot"
        git config user.email "ci@saas.dev"
        git add .
        git commit -m "Deploy backend:${{ github.sha }} to ${{ github.ref_name }}"
        git push
```

---

#### **5.4 Secrets Management**

```yaml
❌ PROBLEMA CRÍTICO:
- .env file em plaintext (nunca commit!)
- Client secret em realm JSON: "saas-local-oauth2-proxy-secret"
- BasicAuth password hardcoded em middlewares.yml
- Test user password: "Test@12345678"

✅ SOLUÇÃO: Vault + ArgoCD integration

# 1. HashiCorp Vault
vault kv put secret/saas-dev/oauth2-proxy \
  client_secret="$(openssl rand -base64 32)"

vault kv put secret/saas-dev/keycloak \
  admin_password="$(openssl rand -base64 20)" \
  db_password="$(openssl rand -base64 20)"

# 2. ArgoCD + Vault plugin
# argocd-repo-server-values.yaml
plugins:
  - name: argocd-vault-plugin
    repository: https://argoproj-labs.github.io/argocd-vault-plugin

# 3. Application manifest
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: saas-prod
spec:
  source:
    repoURL: https://github.com/cotai-eus/saas-gitops
    path: environments/prod
    plugin:
      name: argocd-vault-plugin

# 4. Secret referencing
apiVersion: v1
kind: Secret
metadata:
  name: oauth2-proxy
type: Opaque
stringData:
  client-secret: <path:secret/data/saas-dev/oauth2-proxy#client_secret>

# 5. Docker Secret (single-host production)
docker secret create oauth2_proxy_client_secret -
# Type password, press Enter

# 6. Dockerfile using Docker Secret
FROM quay.io/oauth2-proxy/oauth2-proxy
RUN --mount=type=secret,id=oauth2_proxy_client_secret \
    export OAUTH2_PROXY_CLIENT_SECRET=$(cat /run/secrets/oauth2_proxy_client_secret)
```

---

#### **5.5 CI/CD Pipeline**

```yaml
# .github/workflows/main.yml
name: CI/CD

on:
  push:
    branches: [main, staging, develop]
  pull_request:
    branches: [main, staging, develop]

env:
  REGISTRY: gcr.io
  IMAGE_NAME: saas

jobs:
  # =========================================================================
  # SECURITY SCANNING
  # =========================================================================
  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'
    
    - name: Upload Trivy results
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'
    
    - name: SAST: Run Semgrep
      uses: returntocorp/semgrep-action@v1
      with:
        config: >-
          p/security-audit
          p/owasp-top-ten
          p/python
    
    - name: Dependency check
      uses: dependency-check/Dependency-Check_Action@main
      with:
        project: 'saas'
        path: '.'
  
  # =========================================================================
  # BACKEND TESTS
  # =========================================================================
  backend-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: saas_test
          POSTGRES_PASSWORD: password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
    - uses: actions/checkout@v4
    
    - uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      working-directory: ./backend
      run: |
        python -m pip install --upgrade pip
        pip install poetry
        poetry install
    
    - name: Run tests
      working-directory: ./backend
      env:
        DATABASE_URL: postgresql://postgres:password@localhost:5432/saas_test
      run: |
        poetry run pytest --cov=src tests/
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        files: ./backend/coverage.xml
  
  # =========================================================================
  # FRONTEND TESTS
  # =========================================================================
  frontend-test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - uses: actions/setup-node@v3
      with:
        node-version: '20'
        cache: 'npm'
        cache-dependency-path: './frontend/package-lock.json'
    
    - name: Install dependencies
      working-directory: ./frontend
      run: npm ci
    
    - name: Lint
      working-directory: ./frontend
      run: npm run lint
    
    - name: Type check
      working-directory: ./frontend
      run: npm run type-check
    
    - name: Run tests
      working-directory: ./frontend
      run: npm run test
    
    - name: Build
      working-directory: ./frontend
      run: npm run build
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        files: ./frontend/coverage/coverage-final.json
  
  # =========================================================================
  # BUILD DOCKER IMAGES
  # =========================================================================
  build:
    needs: [backend-test, frontend-test, security]
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    strategy:
      matrix:
        include:
        - dockerfile: backend/Dockerfile
          image: backend
          context: ./backend
        - dockerfile: frontend/Dockerfile
          image: frontend
          context: ./frontend
    
    steps:
    - uses: actions/checkout@v4
    
    - uses: docker/setup-buildx-action@v2
    
    - uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: _json_key
        password: ${{ secrets.GCP_SA_KEY }}
    
    - uses: docker/build-push-action@v5
      with:
        context: ${{ matrix.context }}
        file: ${{ matrix.dockerfile }}
        push: ${{ github.event_name == 'push' && github.ref == 'refs/heads/main' }}
        tags: |
          ${{ env.REGISTRY }}/${{ secrets.GCP_PROJECT }}/${{ matrix.image }}:${{ github.sha }}
          ${{ env.REGISTRY }}/${{ secrets.GCP_PROJECT }}/${{ matrix.image }}:latest
        cache-from: type=registry,ref=${{ env.REGISTRY }}/${{ secrets.GCP_PROJECT }}/${{ matrix.image }}:buildcache
        cache-to: type=registry,ref=${{ env.REGISTRY }}/${{ secrets.GCP_PROJECT }}/${{ matrix.image }}:buildcache,mode=max
        sbom: true
        provenance: true
  
  # =========================================================================
  # HELM LINT
  # =========================================================================
  helm-lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - uses: azure/setup-helm@v3
      with:
        version: '3.13.0'
    
    - name: Lint Helm chart
      run: |
        helm lint helm/
        helm template saas helm/ > /tmp/manifest.yaml
        docker run --rm -i garethr/kubeval:latest < /tmp/manifest.yaml
  
  # =========================================================================
  # DEPLOY TO STAGING
  # =========================================================================
  deploy-staging:
    if: github.event_name == 'push' && github.ref == 'refs/heads/staging'
    needs: build
    runs-on: ubuntu-latest
    environment: staging
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to ArgoCD
      run: |
        # Update GitOps repo with new image SHA
        git clone https://saas-bot:${{ secrets.GITOPS_PAT }}@github.com/cotai-eus/saas-gitops.git
        cd saas-gitops
        
        sed -i "s|${{ env.REGISTRY }}/${{ secrets.GCP_PROJECT }}/backend:.*|${{ env.REGISTRY }}/${{ secrets.GCP_PROJECT }}/backend:${{ github.sha }}|" environments/staging/values.yaml
        sed -i "s|${{ env.REGISTRY }}/${{ secrets.GCP_PROJECT }}/frontend:.*|${{ env.REGISTRY }}/${{ secrets.GCP_PROJECT }}/frontend:${{ github.sha }}|" environments/staging/values.yaml
        
        git config user.name "GitHub Actions"
        git config user.email "actions@github.com"
        git add .
        git commit -m "chore: deploy staging@${{ github.sha }}"
        git push
      env:
        GCP_PROJECT: ${{ secrets.GCP_PROJECT }}
  
  # =========================================================================
  # DEPLOY TO PRODUCTION
  # =========================================================================
  deploy-production:
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    needs: build
    runs-on: ubuntu-latest
    environment: production
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Create GitHub Release
      uses: softprops/action-gh-release@v1
      with:
        tag_name: ${{ github.sha }}
        body: "Deployed to production"
    
    - name: Deploy to ArgoCD
      run: |
        git clone https://saas-bot:${{ secrets.GITOPS_PAT }}@github.com/cotai-eus/saas-gitops.git
        cd saas-gitops
        
        sed -i "s|${{ env.REGISTRY }}/${{ secrets.GCP_PROJECT }}/backend:.*|${{ env.REGISTRY }}/${{ secrets.GCP_PROJECT }}/backend:${{ github.sha }}|" environments/production/values.yaml
        sed -i "s|${{ env.REGISTRY }}/${{ secrets.GCP_PROJECT }}/frontend:.*|${{ env.REGISTRY }}/${{ secrets.GCP_PROJECT }}/frontend:${{ github.sha }}|" environments/production/values.yaml
        
        git config user.name "GitHub Actions"
        git config user.email "actions@github.com"
        git add .
        git commit -m "chore: deploy production@${{ github.sha }}"
        git push
      env:
        GCP_PROJECT: ${{ secrets.GCP_PROJECT }}
```

---

#### **5.6 Observabilidade**

```yaml
❌ PROBLEMA:
- Traefik: prometheus comentado
- Keycloak: KC_METRICS_ENABLED = true, mas não coletado
- Zero centralização de logs
- Sem tracing distribuído
- Sem alertas

✅ SOLUÇÃO: Stack de observabilidade completo

# docker-compose.prod.yml adicionar:

  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    restart: unless-stopped
    networks:
      - proxy
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./monitoring/rules.yml:/etc/prometheus/rules.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

  loki:
    image: grafana/loki:latest
    container_name: loki
    restart: unless-stopped
    networks:
      - proxy
    volumes:
      - ./monitoring/loki.yml:/etc/loki/local-config.yml:ro
      - loki_data:/loki
    command: -config.file=/etc/loki/local-config.yml

  tempo:
    image: grafana/tempo:latest
    container_name: tempo
    restart: unless-stopped
    networks:
      - proxy
    volumes:
      - ./monitoring/tempo.yml:/etc/tempo.yml:ro
      - tempo_data:/var/tempo
    command: -config.file=/etc/tempo.yml

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    restart: unless-stopped
    networks:
      - proxy
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD:?required}
      GF_USERS_ALLOW_SIGN_UP: "false"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources.yml:/etc/grafana/provisioning/datasources/datasources.yml
    labels:
      - "traefik.enable=true"
      - "traefik.docker.network=proxy"
      - "traefik.http.routers.grafana.rule=Host(`grafana.saas.dev`)"
      - "traefik.http.routers.grafana.entrypoints=websecure"
      - "traefik.http.routers.grafana.tls=true"
      - "traefik.http.services.grafana.loadbalancer.server.port=3000"

  # Promtail: coleta logs do Docker para Loki
  promtail:
    image: grafana/promtail:latest
    container_name: promtail
    restart: unless-stopped
    networks:
      - proxy
    volumes:
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock
      - ./monitoring/promtail.yml:/etc/promtail/config.yml
    command: -config.file=/etc/promtail/config.yml
    depends_on:
      - loki

volumes:
  prometheus_data:
  loki_data:
  tempo_data:
  grafana_data:

# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: []

rule_files:
  - '/etc/prometheus/rules.yml'

scrape_configs:
  # Traefik
  - job_name: traefik
    static_configs:
      - targets: ['localhost:8080']

  # Keycloak
  - job_name: keycloak
    static_configs:
      - targets: ['keycloak:9000']
    metrics_path: '/metrics'

  # Backend
  - job_name: backend
    static_configs:
      - targets: ['backend:8001']

  # Prometheus itself
  - job_name: prometheus
    static_configs:
      - targets: ['localhost:9090']

# monitoring/rules.yml
groups:
  - name: saas_alerts
    interval: 30s
    rules:
      - alert: KeycloakDown
        expr: up{job="keycloak"} == 0
        for: 2m
        annotations:
          summary: "Keycloak is down"

      - alert: HighErrorRate
        expr: |
          (
            sum(rate(http_requests_total{status=~"5.."}[5m]))
            /
            sum(rate(http_requests_total[5m]))
          ) > 0.05
        for: 5m
        annotations:
          summary: "High error rate detected"

      - alert: HighLatency
        expr: histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        annotations:
          summary: "High latency detected (p99 > 1s)"
```

---

## **6. BANCO DE DADOS**

### Status: **NÃO ESPECIFICADO**

```
⚠️  CRÍTICO: Não há schema de banco de dados definido.

Assumptions:
- PostgreSQL 14+ (produção-ready)
- SQLAlchemy 2.0 ORM (backend Python)
- Alembic para migrations
```

### 📋 Schema Recomendado

```sql
-- 1. Tenants (Multi-tenancy)
CREATE TABLE tenants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  slug VARCHAR(100) NOT NULL UNIQUE,
  keycloak_realm_id VARCHAR(255) UNIQUE,
  subscription_plan VARCHAR(50) NOT NULL DEFAULT 'starter',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,  -- soft delete
  
  CONSTRAINT tenant_slug_format CHECK (slug ~ '^[a-z0-9-]+$')
);

CREATE INDEX idx_tenants_slug ON tenants(slug);
CREATE INDEX idx_tenants_keycloak_realm_id ON tenants(keycloak_realm_id);
CREATE INDEX idx_tenants_deleted_at ON tenants(deleted_at);

-- Row-Level Security (RLS)
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenants_isolation ON tenants
  USING (id = current_setting('app.current_tenant_id')::uuid);

-- 2. Users (SSO via Keycloak)
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  keycloak_user_id VARCHAR(255) NOT NULL,  -- user.id from Keycloak
  email VARCHAR(255) NOT NULL,
  first_name VARCHAR(255),
  last_name VARCHAR(255),
  roles TEXT[] NOT NULL DEFAULT '{}',  -- ['user', 'admin', ...]
  groups TEXT[] NOT NULL DEFAULT '{}', -- ['/app-users', '/admins', ...]
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  last_login_at TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP,  -- soft delete
  
  CONSTRAINT users_email_per_tenant UNIQUE (tenant_id, email),
  CONSTRAINT users_keycloak_id_unique UNIQUE (tenant_id, keycloak_user_id)
);

CREATE INDEX idx_users_tenant_id ON users(tenant_id);
CREATE INDEX idx_users_keycloak_user_id ON users(keycloak_user_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_deleted_at ON users(deleted_at);

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
CREATE POLICY users_isolation ON users
  USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

-- 3. Audit Logs (compliance)
CREATE TABLE audit_logs (
  id BIGSERIAL PRIMARY KEY,
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  action VARCHAR(50) NOT NULL,  -- 'CREATE', 'UPDATE', 'DELETE', 'LOGIN', etc.
  resource_type VARCHAR(50) NOT NULL,  -- 'tenant', 'user', 'subscription'
  resource_id UUID,
  old_values JSONB,
  new_values JSONB,
  ip_address INET,
  user_agent VARCHAR(500),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_tenant_id ON audit_logs(tenant_id);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);

ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY audit_logs_isolation ON audit_logs
  USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

-- 4. Subscriptions (SaaS billing)
CREATE TABLE subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL UNIQUE REFERENCES tenants(id) ON DELETE CASCADE,
  plan VARCHAR(50) NOT NULL,  -- 'free', 'starter', 'pro', 'enterprise'
  billing_cycle VARCHAR(10) NOT NULL DEFAULT 'monthly',  -- 'monthly', 'annual'
  price_cents BIGINT NOT NULL,
  status VARCHAR(50) NOT NULL DEFAULT 'active',  -- 'active', 'paused', 'canceled'
  seats_limit INTEGER NOT NULL DEFAULT 5,
  started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  trial_ends_at TIMESTAMP,
  renewed_at TIMESTAMP,
  canceled_at TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_subscriptions_tenant_id ON subscriptions(tenant_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_subscriptions_renewed_at ON subscriptions(renewed_at);

-- 5. Sessions (tracking user sessions)
CREATE TABLE sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  keycloak_session_id VARCHAR(255) NOT NULL,
  access_token_jti VARCHAR(500),  -- JWT ID for revocation
  ip_address INET,
  user_agent VARCHAR(500),
  started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_activity_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP NOT NULL,
  ended_at TIMESTAMP,
  
  CONSTRAINT session_not_expired CHECK (expires_at > NOW())
);

CREATE INDEX idx_sessions_tenant_id ON sessions(tenant_id);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_keycloak_session_id ON sessions(keycloak_session_id);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);

-- 6. API Keys (M2M authentication)
CREATE TABLE api_keys (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  key_hash VARCHAR(255) NOT NULL UNIQUE,  -- bcrypt hash
  scopes TEXT[] NOT NULL,  -- ['read:tenants', 'write:users', ...]
  rate_limit INTEGER DEFAULT 1000,  -- requests/hour
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  last_used_at TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP
);

CREATE INDEX idx_api_keys_tenant_id ON api_keys(tenant_id);
CREATE INDEX idx_api_keys_key_hash ON api_keys(key_hash);

-- 7. Feature Flags (gradual rollout)
CREATE TABLE feature_flags (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL UNIQUE,
  description TEXT,
  enabled BOOLEAN NOT NULL DEFAULT FALSE,
  rollout_percentage INTEGER DEFAULT 0,  -- 0-100
  allowed_tenants TEXT[] DEFAULT '{}',  -- specific tenant IDs
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Helper functions
CREATE OR REPLACE FUNCTION set_current_tenant(tenant_id UUID)
RETURNS void AS $$
BEGIN
  PERFORM set_config('app.current_tenant_id', tenant_id::text, true);
END;
$$ LANGUAGE plpgsql;

-- Trigger: update updated_at automatically
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_tenants_updated_at
BEFORE UPDATE ON tenants
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_subscriptions_updated_at
BEFORE UPDATE ON subscriptions
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();

-- Trigger: log all changes to audit_logs
CREATE OR REPLACE FUNCTION audit_changes()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO audit_logs (
    tenant_id, user_id, action, resource_type, resource_id,
    old_values, new_values
  ) VALUES (
    COALESCE(NEW.tenant_id, OLD.tenant_id),
    current_user_id(),
    TG_ARGV[0],
    TG_TABLE_NAME,
    COALESCE(NEW.id, OLD.id),
    to_jsonb(OLD),
    to_jsonb(NEW)
  );
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audit_users
AFTER INSERT OR UPDATE OR DELETE ON users
FOR EACH ROW
EXECUTE FUNCTION audit_changes('users');

-- Migrations with Alembic
-- alembic/versions/001_initial_schema.py
"""Initial schema with multi-tenancy and RLS

Revision ID: 001
Revises: None
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils as sau

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')  # text search
    
    # Tables, indexes, RLS policies, functions...

def downgrade():
    # Cleanup...
```

---

## **7. LACUNAS CRÍTICAS**

### 🚨 **Top 10 Riscos Técnicos**

| # | Risco | Impacto | Probabilidade | Criticidade | Solução |
|---|-------|---------|--------------|-------------|---------|
| **1** | **Sem Backend Python Implementado** | Projeto impossível de usar em produção | MUITO ALTA (99%) | **CRÍTICA** | Implementar backend FastAPI com domain layer, repositories, services (Fase 1 — 4 semanas) |
| **2** | **Sem Frontend React Implementado** | Sem UI para usuários acessarem a aplicação | MUITO ALTA (99%) | **CRÍTICA** | Implementar React + TanStack Query/Router (Fase 1 — 4 semanas) |
| **3** | **`KC_HOSTNAME_STRICT=false`** | Host header injection, IdP spoofing | ALTA (70%) | **CRÍTICA** | Alterar para `true` e validar certificados SSL (30 min) |
| **4** | **`ssl_insecure_skip_verify=true` permanente** | MITM attacks contra Keycloak | ALTA (65%) | **CRÍTICA** | Remover flag em produção; usar CA certificate validation (1 dia) |
| **5** | **Secrets hardcoded em JSON/configs** | Credential exposure se repo vazar | MUITO ALTA (80%) | **CRÍTICA** | Migrar para Vault, Docker Secrets, ou GitHub Secrets (Fase 2 — 1 semana) |
| **6** | **Sem CI/CD / testes automatizados** | Deploy manual, sem rollback automático, regressions | MUITO ALTA (90%) | **ALTA** | Implementar GitHub Actions + pytest + vitest (Fase 1 — 2 semanas) |
| **7** | **Sem Kubernetes readiness** | Impossível escalar para produção | MUITO ALTA (95%) | **CRÍTICA** | Criar Helm charts + K8s manifests (Fase 2 — 2 semanas) |
| **8** | **Multi-tenancy não implementada** | Data leakage entre clientes | ALTA (60%) | **CRÍTICA** | Row-level security, tenant context injection, schema isolamento (Fase 1 — 3 semanas) |
| **9** | **MFA não configurado** | Compromised passwords → account takeover | MUITO ALTA (85%) | **CRÍTICA** | Habilitar TOTP/WebAuthn no Keycloak, enforce MFA (Fase 2 — 1 semana) |
| **10** | **Zero observabilidade (logs, metrics, traces)** | Impossível debugar issues em produção, compliance fail | MUITO ALTA (90%) | **ALTA** | Implementar Prometheus + Grafana + Loki + Tempo (Fase 2 — 1 semana) |

---

## **8. ROADMAP DE EVOLUÇÃO**

### **Fase 1: MVP Sólido (4-6 semanas)**

**Objetivos:**
- Backend Python funcional com autenticação OAuth2
- Frontend React com proteção de rotas
- Database schema multi-tenant
- Testes automatizados (unit + integration)
- Local dev environment rodando

**Refatorações:**
1. Estruturar monorepo com folders `/backend`, `/frontend`, `/infra`
2. Remover hardcoded configs, usar env vars
3. Implementar Dockerfile multi-stage para backend e frontend

**Novos Componentes:**
1. FastAPI application
   - Domain layer (Tenant, User, Subscription models)
   - Application services
   - SQLAlchemy repositories
   - Pydantic schemas
   - Middleware para tenant context

2. React application
   - Feature-based structure
   - TanStack Query + Router
   - Auth provider integration
   - UI components (Material-UI ou shadcn)

3. Database
   - PostgreSQL schema (tenants, users, audit_logs)
   - Alembic migrations
   - Row-level security

4. CI/CD basic
   - GitHub Actions for pytest + vitest
   - Linting + type checking
   - Build Docker images

**Prioridade:** CRÍTICA
**Ganho Esperado:** MVP deployable, basic SaaS functionality

---

### **Fase 2: Produção (2-3 semanas)**

**Objetivos:**
- Security hardening
- Secrets management
- Observabilidade
- Kubernetes readiness
- MFA no Keycloak

**Refatorações:**
1. Migrar secrets para Vault / GitHub Secrets
2. Completar security headers (CSP, etc.)
3. Implementar audit logging
4. Add request tracing (correlation ID)

**Novos Componentes:**
1. Vault integration
   - Dynamic secrets
   - Sealed secrets for K8s

2. OpenTelemetry stack
   - Instrumentation em FastAPI
   - Prometheus metrics
   - Loki for logs
   - Tempo for traces
   - Grafana dashboards

3. Kubernetes
   - Helm charts
   - Deployments, Services, Ingress
   - Network policies
   - Pod disruption budgets
   - HPA (autoscaling)

4. Keycloak production config
   - MFA (TOTP, WebAuthn)
   - Event listeners
   - User federation (LDAP/AD)
   - Theme customization

5. ArgoCD setup
   - GitOps for deployments
   - Automated rollbacks

**Prioridade:** ALTA
**Ganho Esperado:** Production-ready, compliant, observable

---

### **Fase 3: Escala (3-4 semanas)**

**Objetivos:**
- Horizontal scaling (Keycloak, Backend, DB)
- Caching strategy
- Background jobs
- Advanced security features

**Novos Componentes:**
1. Caching layer
   - Redis cluster
   - Cache-aside pattern
   - Invalidation strategy

2. Background jobs
   - Celery + Redis
   - Tasks: email, reports, cleanup

3. Database optimization
   - Connection pooling (pgbouncer)
   - Read replicas
   - Backup strategy
   - Point-in-time recovery

4. API gateway
   - Rate limiting per tenant
   - DDoS protection
   - API versioning

5. Keycloak clustering
   - Distributed caching
   - Database sync
   - Load balancing

6. Advanced auth
   - Custom IdP federation
   - Machine-to-machine (M2M) auth
   - API keys + scopes

**Prioridade:** MÉDIA-ALTA
**Ganho Esperado:** Supports 10K+ concurrent users

---

### **Fase 4: Enterprise SaaS (4-6 semanas)**

**Objetivos:**
- Advanced tenant management
- Billing integration
- Compliance & audit
- Advanced analytics
- Custom branding

**Novos Componentes:**
1. Tenant management
   - Self-service onboarding
   - Tenant admin panel
   - Custom domains (white-label)
   - Isolation verification

2. Billing system
   - Stripe/Paddle integration
   - Usage-based pricing
   - Invoice generation
   - Dunning management

3. Compliance
   - SOC2 compliance
   - GDPR right-to-erasure
   - Data residency
   - Encryption at rest

4. Analytics
   - Event tracking
   - Usage analytics
   - Billing dashboards
   - Tenant insights

5. Customer support
   - Help desk integration (Zendesk)
   - In-app chat
   - Knowledge base

**Prioridade:** BAIXA (business-driven)
**Ganho Esperado:** Enterprise-grade SaaS platform

---

## **9. ARQUITETURA ALVO**

### 🏗️ Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Internet / Browser                          │
└────────────────┬────────────────────────────────────────────────────┘
                 │
          ┌──────▼──────────────────┐
          │  CloudFlare (optional)   │
          │  - DDoS protection       │
          │  - WAF                   │
          └──────┬───────────────────┘
                 │ HTTPS
          ┌──────▼──────────────────────────────────────────────────┐
          │         Load Balancer (Cloud: GCP LB / AWS ALB)         │
          │         - SSL termination                               │
          │         - Health checks                                 │
          │         - Auto-scaling trigger                          │
          └──────┬───────────────────────────────────────────────────┘
                 │
    ┌────────────┼────────────┬────────────┐
    │            │            │            │
    ▼            ▼            ▼            ▼
┌─────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐
│ Traefik │ │ Keycloak │ │  Backend │ │Frontend │
│ Ingress │ │   Auth   │ │  FastAPI │ │ React   │
│   ×3    │ │    ×3    │ │    ×3    │ │  ×2    │
└────┬────┘ └────┬─────┘ └────┬─────┘ └────┬────┘
     │           │            │            │
     └───────────┼────────────┼────────────┘
                 │            │
        ┌────────▼────┐ ┌────▼──────────────┐
        │ PostgreSQL  │ │   Redis Cluster   │
        │  Primary    │ │   - Cache         │
        │     +       │ │   - Sessions      │
        │  Replica    │ │   - Celery queue  │
        └─────────────┘ └───────────────────┘
             │
        ┌────▼──────────┐
        │  S3 / GCS     │
        │  - Backups    │
        │  - Artifacts  │
        └───────────────┘

Observability Stack:
┌──────────────────────────────────────────────────┐
│                  Kubernetes Cluster               │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │Prometheus│  │   Loki   │  │    Tempo     │  │
│  │  Metrics │  │   Logs   │  │   Traces     │  │
│  └────┬─────┘  └────┬─────┘  └────┬────────┘  │
│       │             │             │           │
│       └─────────────┼─────────────┘           │
│                     │                         │
│              ┌──────▼────────┐               │
│              │    Grafana    │               │
│              │  Dashboards   │               │
│              └───────────────┘               │
│                     │                         │
│              ┌──────▼────────┐               │
│              │  AlertManager │               │
│              │   (Slack)     │               │
│              └───────────────┘               │
└──────────────────────────────────────────────────┘

CI/CD Pipeline:
┌─────────────────────────────────────────────────┐
│   GitHub Repository (GitOps)                    │
│   - Source code                                 │
│   - Helm charts                                 │
│   - K8s manifests                               │
└────────────┬────────────────────────────────────┘
             │
      ┌──────▼─────────────┐
      │  GitHub Actions    │
      │  - Unit tests      │
      │  - Integration     │
      │  - Security scan   │
      │  - Build docker    │
      │  - Push to GCR     │
      └──────┬─────────────┘
             │
      ┌──────▼─────────────┐
      │   ArgoCD / Flux    │
      │   - GitOps sync    │
      │   - Auto-deploy    │
      │   - Rollbacks      │
      └──────┬─────────────┘
             │
      ┌──────▼─────────────┐
      │  Kubernetes        │
      │  - Run workloads   │
      │  - Health checks   │
      │  - Rolling updates │
      └────────────────────┘
```

---

### **Fluxos Detalhados**

#### **1. Fluxo de Autenticação**

```
┌─────────────────────────────────────────────────────────┐
│  User accesses https://app.saas.dev                     │
└──────────────────┬──────────────────────────────────────┘
                   │
         ┌─────────▼──────────┐
         │  Frontend (React)   │
         │  - Check session    │
         │  - No token found   │
         └─────────┬──────────┘
                   │
         ┌─────────▼──────────────────────────┐
         │  Redirect to /auth/login           │
         │  Keycloak OAuth2 authorization_url │
         └─────────┬──────────────────────────┘
                   │
         ┌─────────▼──────────────────────────┐
         │  Browser → Keycloak /auth/authorize │
         │  - client_id: oauth2-proxy         │
         │  - redirect_uri: app.saas.dev/...  │
         │  - scope: openid profile email     │
         │  - code_challenge (PKCE)           │
         └─────────┬──────────────────────────┘
                   │
         ┌─────────▼──────────────────────────┐
         │  Keycloak renders login form        │
         │  (supports password, TOTP, etc.)   │
         └─────────┬──────────────────────────┘
                   │
         ┌─────────▼──────────────────────────┐
         │  User enters credentials + MFA     │
         │  (TOTP code if enabled)            │
         └─────────┬──────────────────────────┘
                   │
         ┌─────────▼──────────────────────────┐
         │  Keycloak validates + creates tokens│
         │  - Authorization Code (short-lived)│
         └─────────┬──────────────────────────┘
                   │
         ┌─────────▼──────────────────────────┐
         │  Redirect to /oauth2/callback       │
         │  + auth code                       │
         │  (via OAuth2-Proxy endpoint)       │
         └─────────┬──────────────────────────┘
                   │
         ┌─────────▼──────────────────────────┐
         │  OAuth2-Proxy exchanges code       │
         │  for tokens (backend call)         │
         │  - ID Token (JWT)                  │
         │  - Access Token (JWT)              │
         │  - Refresh Token                   │
         └─────────┬──────────────────────────┘
                   │
         ┌─────────▼──────────────────────────┐
         │  OAuth2-Proxy creates session      │
         │  Sets cookie:                      │
         │  _oauth2_proxy=<encrypted session> │
         └─────────┬──────────────────────────┘
                   │
         ┌─────────▼──────────────────────────┐
         │  Browser stores cookie             │
         │  (HttpOnly, Secure, SameSite=Lax)  │
         └─────────┬──────────────────────────┘
                   │
         ┌─────────▼──────────────────────────┐
         │  Redirect to /dashboard            │
         │  Subsequent requests include       │
         │  _oauth2_proxy cookie              │
         └─────────┬──────────────────────────┘
                   │
         ┌─────────▼──────────────────────────┐
         │  Traefik ForwardAuth checks cookie │
         │  via OAuth2-Proxy /oauth2/auth     │
         │  ✅ Valid → allow request          │
         └─────────┬──────────────────────────┘
                   │
         ┌─────────▼──────────────────────────┐
         │  Traefik injects headers:          │
         │  - X-Auth-Request-User             │
         │  - X-Auth-Request-Email            │
         │  - X-Auth-Request-Groups           │
         │  - X-Tenant-ID (custom)            │
         └─────────┬──────────────────────────┘
                   │
         ┌─────────▼──────────────────────────┐
         │  Backend receives request          │
         │  extracts tenant context           │
         │  queries database for tenant data  │
         │  applies row-level security        │
         └─────────┬──────────────────────────┘
                   │
         ┌─────────▼──────────────────────────┐
         │  Backend returns 200 + data        │
         │  Frontend renders page             │
         └─────────────────────────────────────┘
```

---

#### **2. Fluxo de Logout**

```
┌─────────────────────────────────────┐
│  User clicks logout button          │
└──────────────┬──────────────────────┘
               │
     ┌─────────▼──────────────────────┐
     │  Frontend calls /oauth2/sign_out │
     │  (OAuth2-Proxy endpoint)        │
     └─────────┬──────────────────────┘
               │
     ┌─────────▼──────────────────────┐
     │  OAuth2-Proxy:                 │
     │  - Invalidates session cookie   │
     │  - Calls Keycloak /logout       │
     │  - Logs audit event             │
     └─────────┬──────────────────────┘
               │
     ┌─────────▼──────────────────────┐
     │  Keycloak:                     │
     │  - Invalidates tokens          │
     │  - Revokes refresh token       │
     │  - Clears session              │
     └─────────┬──────────────────────┘
               │
     ┌─────────▼──────────────────────┐
     │  Redirect to login page        │
     │  Clear cookies                 │
     │  Clear local storage           │
     └────────────────────────────────┘
```

---

#### **3. Fluxo de API (M2M) com JWT Bearer**

```
┌────────────────────────────────────────┐
│  External service calls API            │
│  GET /api/v1/tenants                   │
│  Authorization: Bearer <JWT>           │
└─────────────┬────────────────────────┘
              │
    ┌─────────▼─────────────────────────┐
    │  Backend receives request          │
    │  Extracts JWT from Auth header     │
    └─────────┬────────────────────────┘
              │
    ┌─────────▼─────────────────────────┐
    │  Validates JWT signature:          │
    │  - Fetches JWKS from Keycloak     │
    │  - Verifies iss, aud, exp         │
    │  - Extracts claims (tenant_id)    │
    └─────────┬────────────────────────┘
              │
    ┌─────────▼─────────────────────────┐
    │  Extracts tenant context          │
    │  Queries with RLS enabled         │
    │  Only returns tenant data         │
    └─────────┬────────────────────────┘
              │
    ┌─────────▼─────────────────────────┐
    │  Returns 200 + JSON response      │
    │  Logs to audit_logs               │
    └────────────────────────────────────┘
```

---

## **10. RESULTADO EXECUTIVO**

### **Nota Geral: 5.5/10**

**Status:** Infraestrutura de autenticação bem estruturada, mas **zero aplicação implementada**. Prototipo dev-only, não pronto para produção.

---

### **Principais Forças** ✅

1. **OAuth2/OIDC corretamente implementado**
   - Authorization Code Flow com PKCE
   - Audience claim validation
   - Groups/roles mapeamento
   - Access token lifecycle correto

2. **Security best practices sólidos**
   - TLS obrigatório (HTTPS redirect)
   - Headers OWASP aplicados (HSTS, CSP, X-Frame-Options)
   - Cookies HttpOnly + Secure + SameSite
   - Docker networking isolado (internal network)
   - Menor privilégio no Traefik (`exposedByDefault: false`)

3. **Docker & infra bem estruturados**
   - Imagens com SHA256 pinned
   - Health checks implementados
   - Docker Compose lógico com volumes nomeados
   - Setup script automatiza bootstrap

4. **Documentação adequada**
   - README claro com fluxo de autenticação
   - Comandos úteis para troubleshooting
   - Arquivos de configuração bem comentados

5. **Keycloak production-ready features**
   - Brute force protection habilitado
   - Health endpoints implementados
   - Métricas disponíveis
   - Realm export/import suportado

---

### **Principais Fraquezas** ❌

1. **APLICAÇÃO AUSENTE**
   - Sem backend Python (FastAPI, Django, Flask)
   - Sem frontend React/Vue/Angular
   - Sem banco de dados de negócio
   - Sem lógica de SaaS (tenants, billing, etc.)

2. **Segurança crítica**
   - `KC_HOSTNAME_STRICT=false` (host header injection)
   - `ssl_insecure_skip_verify=true` permanente (MITM)
   - Secrets hardcoded (client_secret em JSON, admin password em yaml)
   - MFA não implementado
   - CSP truncado/incompleto

3. **Infra para produção**
   - Sem CI/CD (GitHub Actions)
   - Sem Kubernetes/Helm
   - Sem observabilidade (Prometheus/Grafana comentado, sem Loki/Tempo)
   - Docker Compose não versiona ENV vars
   - Sem secrets management (Vault/sealed-secrets)

4. **Escalabilidade**
   - Single Keycloak instance
   - Sem Redis/caching
   - Sem connection pooling
   - Sem async jobs (Celery)
   - Sem load balancing entre réplicas

5. **Multi-tenancy**
   - Zero implementação
   - Sem tenant context extraction
   - Sem row-level security no DB
   - Sem isolamento de dados

6. **Testes & qualidade**
   - Zero testes automatizados
   - Sem linting ou type-checking
   - Sem code coverage
   - Setup.sh é manual e frágil

---

### **Quick Wins (30 dias)**

| Item | Esforço | Impacto | Prioridade |
|------|---------|--------|-----------|
| Remover `ssl_insecure_skip_verify=true` | 1 dia | CRÍTICO | 🔴 P0 |
| Alterar `KC_HOSTNAME_STRICT=false` → `true` | 1 dia | CRÍTICO | 🔴 P0 |
| Migrar secrets para .env.example + GitHub Secrets | 3 dias | CRÍTICO | 🔴 P0 |
| Implementar setup.sh com validações | 2 dias | ALTO | 🟠 P1 |
| Add GitHub Actions basic CI (lint + test shell scripts) | 2 dias | ALTO | 🟠 P1 |
| Documentar passos manuais em README | 1 dia | MÉDIO | 🟡 P2 |
| Enable Prometheus metrics no Traefik | 1 dia | MÉDIO | 🟡 P2 |
| Completar CSP header | 1 dia | MÉDIO | 🟡 P2 |
| **Total** | **~12 dias** | - | - |

---

### **Melhorias Médio Prazo (90 dias)**

#### **Semana 1-2: Backend MVP**
```
- Scaffold FastAPI com Pydantic v2
- SQLAlchemy 2.0 setup + Alembic
- Domain models: Tenant, User, Subscription
- Repository pattern
- OAuth2/OIDC integration (via Keycloak)
- Health check endpoint
- Pytest setup com fixtures
Ganho: Backend deployable com autenticação
```

#### **Semana 3-4: Frontend MVP**
```
- Vite + React 18 setup
- TanStack Router + Query
- Auth provider integration
- Protected route wrapper
- Basic dashboard
- Vitest + Testing Library
Ganho: Frontend com SSO integrado
```

#### **Semana 5-6: Database & Multi-Tenancy**
```
- PostgreSQL schema completo
- RLS (Row-Level Security) policies
- Audit logging triggers
- Alembic migrations
- Connection pooling (pgbouncer)
Ganho: Data isolation garantida
```

#### **Semana 7-8: Observability & Security**
```
- Prometheus + Grafana stack
- Loki for centralized logs
- Tempo for distributed tracing
- OpenTelemetry instrumentation
- Vault for secrets
- SecurityScan (Trivy) em CI
Ganho: Full observability + secret management
```

#### **Semana 9-10: Kubernetes & GitOps**
```
- Helm charts para todos os componentes
- K8s manifests (Deployment, Service, Ingress, HPA)
- Network policies
- PodDisruptionBudgets
- ArgoCD setup
Ganho: Production-ready on K8s
```

#### **Semana 11-12: Hardening**
```
- MFA no Keycloak (TOTP + WebAuthn)
- Rate limiting aprimorado
- API key management
- CORS setup correto
- Helmet.js headers (React)
- Load test & benchmark
Ganho: Production secure & performant
```

---

### **Visão 12 Meses**

#### **Q1 (Jan-Mar): Foundation**
- ✅ Backend com domain logic
- ✅ Frontend com UI completo
- ✅ Database schema + RLS
- ✅ Basic CI/CD
- ✅ Single-tenant working
- **Users:** 10-50
- **Regions:** 1 (local)

#### **Q2 (Apr-Jun): Scale & Security**
- ✅ Multi-tenant architecture
- ✅ Kubernetes cluster (3 nodes)
- ✅ Observability stack
- ✅ MFA implementation
- ✅ Stripe billing integration
- ✅ SOC2 audit start
- **Users:** 100-500
- **Regions:** 1 (cloud)

#### **Q3 (Jul-Sep): Enterprise Features**
- ✅ Custom domains (white-label)
- ✅ Advanced RBAC/ABAC
- ✅ Audit compliance reports
- ✅ Data residency (US/EU)
- ✅ Auto-scaling (20 pods)
- ✅ CDN for frontend
- **Users:** 500-2K
- **Regions:** 2 (US + EU)

#### **Q4 (Oct-Dec): Production Scale**
- ✅ Multi-region failover
- ✅ Advanced analytics
- ✅ Help desk integration
- ✅ API ecosystem
- ✅ Marketplace
- ✅ Certifications (SOC2, ISO27001)
- **Users:** 2K-10K
- **Regions:** 3+ (global)

---

### **Conclusão**

Este repositório é um **excelente ponto de partida de infraestrutura**, mas **totalmente insuficiente como um SaaS completo**. 

**Ações imediatas (próximas 30 dias):**

1. **Remover vulnerabilidades críticas** de segurança (SSL verify, hostname strict)
2. **Implementar backend Python** (FastAPI scaffold)
3. **Implementar frontend React** (basic auth flow)
4. **Setup CI/CD básico** (GitHub Actions)
5. **Migrar secrets** para Vault/GitHub Secrets
6. **Documentar arquitetura alvo** (ADRs)

**Estimativa total para MVP funcional:** 8-12 semanas  
**Estimativa para produção enterprise:** 6-9 meses

O roadmap de 4 fases acima fornece um caminho claro. A prioridade deve ser **reduzir o risco de segurança crítica** enquanto **incrementa valor funcional** em paralelo.