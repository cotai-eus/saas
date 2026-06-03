from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from middleware.auth import JWTAuthMiddleware, fetch_jwks
from api.routers import health, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    await fetch_jwks()
    yield


app = FastAPI(title="SaaS Backend", lifespan=lifespan)
app.add_middleware(JWTAuthMiddleware)

app.include_router(health.router)
app.include_router(auth.router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
