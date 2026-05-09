"""FastAPI 中间件 — 请求限流 / 安全头 / 会话清理"""

import time

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.security import check_rate_limit, sanitize_input, should_purge_session, _token_sessions

logger = structlog.get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """按 IP 限流中间件：同一 IP 每分钟最多 20 次（configurable）"""

    async def dispatch(self, request: Request, call_next):
        # Skip health check and docs
        if request.url.path in ("/api/v1/health", "/docs", "/redoc", "/openapi.json"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"

        if not check_rate_limit(client_ip, max_requests=20, window=60):
            logger.warning("rate_limit_exceeded", ip=client_ip, path=request.url.path)
            return JSONResponse(
                status_code=429,
                content={"detail": "请求过于频繁，请稍后再试"},
            )

        return await call_next(request)


class InputSanitizationMiddleware(BaseHTTPMiddleware):
    """对 JSON body 中的 'content' 和 'message' 字段自动清洗"""

    async def dispatch(self, request: Request, call_next):
        if request.method in ("POST", "PUT", "PATCH"):
            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type:
                try:
                    body = await request.json()
                    cleaned = False

                    def _clean(obj):
                        nonlocal cleaned
                        if isinstance(obj, dict):
                            for key in ("content", "message", "text", "note"):
                                if key in obj and isinstance(obj[key], str):
                                    orig = obj[key]
                                    obj[key] = sanitize_input(obj[key])
                                    if orig != obj[key]:
                                        cleaned = True
                            for v in obj.values():
                                _clean(v)
                        elif isinstance(obj, list):
                            for item in obj:
                                _clean(item)

                    _clean(body)

                    if cleaned:
                        from starlette.datastructures import Headers
                        import json as _json
                        from io import BytesIO

                        body_bytes = _json.dumps(body).encode("utf-8")
                        request._body = body_bytes
                        request.headers = Headers({
                            **dict(request.headers),
                            "content-length": str(len(body_bytes)),
                        })
                except Exception:
                    pass

        return await call_next(request)


async def purge_expired_sessions():
    """清理超过保留期的匿名会话（应在后台定时任务中调用）"""
    now = time.time()
    expired = [t for t, s in _token_sessions.items() if should_purge_session(s["created_at"])]
    for t in expired:
        del _token_sessions[t]
    if expired:
        logger.info("purged_expired_sessions", count=len(expired))
    return len(expired)
