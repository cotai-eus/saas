# SaaS Backend

Multi-tenant messaging platform (WhatsApp) built with FastAPI + PostgreSQL + Keycloak.

```
src/
├── main.py                         # FastAPI app, lifespan, middleware, exception handlers
├── api/routers/                    # Route handlers — health, auth, channels, messages, contacts, webhooks
├── application/                    # Use cases / services — send_message, create_channel, billing/quota
├── domain/                         # Domain entities & exceptions — Channel, Message, value objects
├── infrastructure/
│   ├── settings.py                 # pydantic-settings shared with Alembic
│   ├── queue/                      # Redis queue producer for async message delivery
│   ├── providers/                  # Provider abstractions (WhatsApp Official, Baileys, etc.)
│   ├── crypto.py                   # Config encryption helpers
│   └── database/
│       ├── session.py              # Engine, scoped session, get_db() with RLS config
│       ├── base.py                 # SQLAlchemy DeclarativeBase
│       └── models/                 # ORM models (channel, message, contact, tenant, subscription...)
└── middleware/auth.py              # JWTAuthMiddleware with JWKS RS256 verification
```

## API Endpoints (`/api/v1`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/health` | No | Health check |
| `GET` | `/me` | No (optional) | JWT claims debug |
| `POST` | `/channels/` | JWT | Create channel → **201** |
| `GET` | `/channels/` | JWT | List channels (paginated) |
| `GET` | `/channels/{id}` | JWT | Get channel |
| `PUT` | `/channels/{id}` | JWT | Update channel |
| `DELETE` | `/channels/{id}` | JWT | Delete channel → **204** |
| `POST` | `/channels/{id}/validate` | JWT | Validate channel config |
| `GET` | `/channels/{id}/qr` | JWT | Get WhatsApp QR code |
| `POST` | `/messages/` | JWT | Send message → **201** |
| `GET` | `/messages/` | JWT | List messages (paginated, sortable) |
| `GET` | `/messages/{id}` | JWT | Get message details |
| `POST` | `/contacts/` | JWT | Create contact → **201** |
| `GET` | `/contacts/` | JWT | List contacts (paginated, sortable) |
| `GET` | `/contacts/{id}` | JWT | Get contact details |
| `GET` | `/templates/` | JWT | List templates (stub — 501) |
| `POST` | `/webhooks/{type}/{id}` | HMAC | Inbound message/status webhook |
| `GET` | `/webhooks/whatsapp_official/{id}` | Token | Meta webhook verification |

## Architecture

- **Layered**: routes → use cases (`application/`) → domain entities (`domain/`)
- **Multi-tenancy**: PostgreSQL RLS via `app.current_tenant_id` session variable
- **Auth**: JWT Bearer via middleware, RS256 + JWKS from Keycloak; tenant scoped by `get_tenant_id()` dependency
- **Queue**: Redis-backed for async message dispatch
- **Pagination**: Uniform `?limit=50&offset=0` + `{"total": N, "items": [...]}`
- **Sorting**: `?sort_by=created_at&sort_order=desc` on list endpoints
- **Status codes**: 201 on creation, 204 on deletion, 409 on conflict, 422 on validation, 429 on quota exceeded
- **Errors**: Consistent `{"detail": "..."}` via FastAPI exception handlers
- **Settings**: `pydantic-settings` shared with Alembic

Acessível em `https://api.{domain}` via Traefik (atrás do OAuth2-Proxy).
