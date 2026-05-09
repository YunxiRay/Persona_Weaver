import asyncio

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.config import router as config_router
from app.api.routes.report import router as report_router
from app.api.routes.session import router as session_router
from app.api.ws.chat import chat_websocket
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import RateLimitMiddleware, InputSanitizationMiddleware, purge_expired_sessions

setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    docs_url="/docs" if settings.APP_DEBUG else None,
    redoc_url="/redoc" if settings.APP_DEBUG else None,
)

# Middleware order: CORS → RateLimit → InputSanitization
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(InputSanitizationMiddleware)

app.include_router(config_router, prefix=settings.API_PREFIX)
app.include_router(session_router, prefix=settings.API_PREFIX)
app.include_router(report_router, prefix=settings.API_PREFIX)


@app.on_event("startup")
async def startup():
    # Periodic session cleanup (every 3600s)
    async def _cleanup_loop():
        while True:
            await asyncio.sleep(3600)
            await purge_expired_sessions()

    asyncio.create_task(_cleanup_loop())


@app.get(f"{settings.API_PREFIX}/health")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.APP_ENV}


@app.websocket("/ws/chat")
async def ws_chat(ws: WebSocket):
    await chat_websocket(ws)
