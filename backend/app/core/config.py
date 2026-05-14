import json

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── 应用 ──
    APP_NAME: str = "persona-weaver"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    API_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ── 数据库 ──
    DATABASE_URL: str = "sqlite+aiosqlite:///./persona_weaver.db"

    # ── LLM ──
    DEV_LLM_PROVIDER: str = "deepseek"
    DEV_LLM_API_KEY: str = ""
    DEV_LLM_BASE_URL: str = "https://api.deepseek.com"
    DEV_LLM_MODEL: str = "deepseek-v4-flash"
    DEV_LLM_MAX_RETRIES: int = 3
    DEV_LLM_REQUEST_TIMEOUT: int = 30

    # ── 推理引擎 ──
    INFERENCE_CONVERGENCE_THRESHOLD: float = 0.08
    INFERENCE_MIN_EFFECTIVE_WORDS: int = 300
    INFERENCE_MAX_TURNS: int = 50
    INFERENCE_LIGHT_REPORT_WORDS: int = 600

    # ── 安全 ──
    SECRET_KEY: str = "change-me-in-production"
    CRISIS_KEYWORDS: str = "自杀,自伤,结束生命,不想活,自残,伤害自己"
    CRISIS_HELPLINE: str = "心理援助热线：12320（24小时）"

    # ── CORS ──
    CORS_ORIGINS: list[str] = ["*"]

    # ── 日志 ──
    LOG_LEVEL: str = "DEBUG"
    LOG_FORMAT: str = "json"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
