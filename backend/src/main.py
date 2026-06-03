from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from middleware.auth import JWTAuthMiddleware, fetch_jwks
from middleware.tenant import TenantContextMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    await fetch_jwks()
    yield


app = FastAPI(title="SaaS Backend", lifespan=lifespan)
app.add_middleware(TenantContextMiddleware)
app.add_middleware(JWTAuthMiddleware)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/me")
async def me(request: Request):
    return {
        "user_id": getattr(request.state, "user_id", None),
        "email": getattr(request.state, "email", None),
        "tenant_id": getattr(request.state, "tenant_id", None),
        "roles": getattr(request.state, "roles", []),
        "groups": getattr(request.state, "groups", []),
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )