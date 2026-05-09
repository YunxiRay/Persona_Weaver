"""安全模块 — API 鉴权 / 请求限流 / 输入清洗 / 危机关键词检测"""

import re
import time
import uuid
from collections import defaultdict

import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)

# ── Simple Session Token ──

_token_sessions: dict[str, dict] = {}


def create_session_token() -> str:
    token = str(uuid.uuid4())
    _token_sessions[token] = {"created_at": time.time(), "last_active": time.time()}
    return token


def validate_session_token(token: str) -> bool:
    session = _token_sessions.get(token)
    if not session:
        return False
    session["last_active"] = time.time()
    return True


# ── Rate Limiting ──

_rate_limit_store: dict[str, list[float]] = defaultdict(list)


def check_rate_limit(identifier: str, max_requests: int = 20, window: int = 60) -> bool:
    """基于滑动窗口的请求限流。返回 True 表示允许，False 表示限流"""
    now = time.time()
    window_start = now - window
    _rate_limit_store[identifier] = [t for t in _rate_limit_store[identifier] if t > window_start]
    if len(_rate_limit_store[identifier]) >= max_requests:
        return False
    _rate_limit_store[identifier].append(now)
    return True


# ── Input Sanitization ──

XSS_PATTERN = re.compile(r"<script|javascript:|onerror=|onload=", re.IGNORECASE)
SQL_INJECTION_PATTERN = re.compile(
    r"(\bSELECT\b.*\bFROM\b|\bDROP\b|\bDELETE\b|\bINSERT\b|\bUPDATE\b|\bUNION\b.*\bSELECT\b)",
    re.IGNORECASE,
)


def sanitize_input(text: str) -> str:
    """清洗用户输入：去除 XSS/SQL 注入风险"""
    text = XSS_PATTERN.sub("[filtered]", text)
    text = SQL_INJECTION_PATTERN.sub("[filtered]", text)
    if len(text) > 10000:
        text = text[:10000]
    return text


# ── Crisis Detection ──

CRISIS_KEYWORDS = [k.strip() for k in settings.CRISIS_KEYWORDS.split(",") if k.strip()]


def detect_crisis(text: str) -> dict:
    """检测用户输入中的危机关键词，返回风险级别和命中的关键词"""
    hits = [k for k in CRISIS_KEYWORDS if k in text]
    if hits:
        logger.warning("crisis_keywords_detected", keywords=hits)
        return {"risk_level": "HIGH", "trigger_keywords": hits, "helpline": settings.CRISIS_HELPLINE}
    return {"risk_level": "LOW", "trigger_keywords": [], "helpline": ""}


# ── Privacy: Data Retention ──

def should_purge_session(session_created_at: float, retention_days: int = 7) -> bool:
    """检查匿名会话是否超过保留期（默认 7 天）"""
    return time.time() - session_created_at > retention_days * 86400


# ── Input Validation ──

# Minimum content length for meaningful input
MIN_CONTENT_LENGTH = 2
MAX_INPUT_LENGTH = 5000
NOISE_PATTERN = re.compile(r"^[\s\.\,\!\?\;\:]+$")


def validate_user_input(text: str) -> str | None:
    """验证用户输入有效性。返回错误消息或 None（表示有效）"""
    if len(text) < MIN_CONTENT_LENGTH:
        return "请多说一些，让我更好地了解你"
    if len(text) > MAX_INPUT_LENGTH:
        return "输入太长，请精简一些再发送"
    if NOISE_PATTERN.match(text):
        return "请用文字表达你的想法"
    unique_chars = len(set(text))
    if unique_chars <= 1 and len(text) >= 4:
        return "请用完整的句子来表达"
    return None
