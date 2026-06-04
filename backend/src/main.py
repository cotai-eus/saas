import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from middleware.auth import ProxyAuthMiddleware
from api.routers import health, auth, channels, messages, webhooks, contacts, templates
from infrastructure.settings import settings

logger = logging.getLogger(__name__)

API_PREFIX = "/api/v1"

app = FastAPI(title="SaaS Backend", redirect_slashes=False)

app.add_middleware(ProxyAuthMiddleware)

app.include_router(health.router)
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(channels.router, prefix=API_PREFIX)
app.include_router(messages.router, prefix=API_PREFIX)
app.include_router(contacts.router, prefix=API_PREFIX)
app.include_router(templates.router, prefix=API_PREFIX)
app.include_router(webhooks.router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
