# SaaS Backend

```
src/
├── main.py                         # FastAPI app, lifespan, middleware, exception handlers
├── api/routers/                    # Route handlers (health, auth, ...)
├── application/                    # Use cases / services (placeholder)
├── domain/                         # Domain entities / logic (placeholder)
├── infrastructure/
│   ├── settings.py                 # pydantic-settings shared with Alembic
│   └── database/
│       ├── session.py              # Engine, scoped session, get_db() with RLS config
│       ├── base.py                 # SQLAlchemy DeclarativeBase
│       └── models/                 # ORM models (tenant, user, subscription, ...)
└── middleware/auth.py              # JWTAuthMiddleware
```

Layered architecture: routes call `Depends(get_db)` for DB access — no session opened otherwise. JWT auth via `JWTAuthMiddleware` with JWKS cache. Settings via `pydantic-settings`, shared with Alembic.

Acessível em `https://api.{domain}` via Traefik (atrás do OAuth2-Proxy).
