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
    DATABASE_URL: str = "postgresql+asyncpg://persona:persona_dev@localhost:5432/persona_weaver"
    DATABASE_URL_SYNC: str = "postgresql://persona:persona_dev@localhost:5432/persona_weaver"

    # ── Redis ──
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── LLM ──
    DEV_LLM_PROVIDER: str = "deepseek"
    DEV_LLM_API_KEY: str = ""
    DEV_LLM_BASE_URL: str = "https://api.deepseek.com/v1"
    DEV_LLM_MODEL: str = "deepseek-chat"
    DEV_LLM_MAX_RETRIES: int = 3
    DEV_LLM_REQUEST_TIMEOUT: int = 30

    # ── 嵌入模型 ──
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-large-zh-v1.5"

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
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    # ── 日志 ──
    LOG_LEVEL: str = "DEBUG"
    LOG_FORMAT: str = "json"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
