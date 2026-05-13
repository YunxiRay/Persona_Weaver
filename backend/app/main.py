import asyncio
import os
import sys

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes.config import router as config_router
from app.api.routes.data import router as data_router
from app.api.routes.debug import router as debug_router
from app.api.routes.report import router as report_router
from app.api.routes.session import router as session_router
from app.api.ws.chat import chat_websocket
from app.core.config import settings
from app.core.database import Base, get_engine
from app.core.logging import setup_logging
from app.core.middleware import RateLimitMiddleware, InputSanitizationMiddleware, purge_expired_sessions
from app.core.persistence import load_config, load_reports, save_config, save_reports, save_sessions, load_sessions

setup_logging()

import structlog
logger = structlog.get_logger()

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

@app.get(f"{settings.API_PREFIX}/health")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.APP_ENV}


@app.websocket("/ws/chat")
async def ws_chat(ws: WebSocket):
    await chat_websocket(ws)


app.include_router(config_router, prefix=settings.API_PREFIX)
app.include_router(data_router, prefix=settings.API_PREFIX)
app.include_router(debug_router, prefix=settings.API_PREFIX)
app.include_router(session_router, prefix=settings.API_PREFIX)
app.include_router(report_router, prefix=settings.API_PREFIX)


@app.on_event("startup")
async def startup():
    # 0. Auto-create SQLite tables
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 1. Restore persisted config
    try:
        from app.api.routes.config import _config_store
        from app.llm.provider import ProviderConfig

        saved_config = load_config()
        if saved_config:
            _config_store["default"] = ProviderConfig(**saved_config)
            logger.info("config_restored")
    except Exception:
        logger.warning("config_restore_failed", exc_info=True)

    # 2. Restore persisted reports
    try:
        from app.engine.chat_pipeline import _reports

        saved_reports = load_reports()
        if saved_reports:
            _reports.update(saved_reports)
            logger.info("reports_restored", count=len(saved_reports))
    except Exception:
        logger.warning("reports_restore_failed", exc_info=True)

    # 3. Periodic session cleanup (every 3600s)
    async def _cleanup_loop():
        while True:
            await asyncio.sleep(3600)
            await purge_expired_sessions()

    asyncio.create_task(_cleanup_loop())


@app.on_event("shutdown")
async def shutdown():
    try:
        from app.api.routes.config import _config_store
        from app.engine.chat_pipeline import _sessions, _reports

        save_config(_config_store.get("default"))
        save_reports(_reports)
        save_sessions(_sessions)
        logger.info("data_persisted_on_shutdown")
    except Exception:
        logger.warning("shutdown_persist_failed", exc_info=True)


# Serve frontend static files — MUST be last (lowest priority)
if getattr(sys, "frozen", False):
    STATIC_DIR = os.path.join(sys._MEIPASS, "static")
else:
    STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
