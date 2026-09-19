from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.config.settings import get_settings
from app.database.connection import delete_expired_conversations, initialize_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    delete_expired_conversations(get_settings().conversation_retention_days)
    yield


app = FastAPI(
    title="API de Atendimento da Empresa",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=get_settings().allowed_host_list,
)


@app.middleware("http")
async def require_secure_transport(request: Request, call_next):
    settings = get_settings()
    if settings.require_https and request.url.scheme != "https":
        return JSONResponse(
            status_code=426,
            content={"detail": "HTTPS e obrigatorio para este servico."},
        )
    response = await call_next(request)
    if settings.require_https:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response
app.include_router(router)


@app.get("/health", tags=["operacao"])
def health() -> dict[str, str]:
    return {"status": "ok"}