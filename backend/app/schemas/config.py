from pydantic import BaseModel


class LLMConfigRequest(BaseModel):
    provider: str  # deepseek | qwen | glm | moonshot | openai_compatible
    api_key: str
    model: str | None = None
    base_url: str | None = None


class LLMConfigResponse(BaseModel):
    provider: str
    api_key: str  # masked, only last 4 chars shown
    model: str
    base_url: str
    is_configured: bool


class TestConnectionResponse(BaseModel):
    success: bool
    provider: str
    error: str | None = None
