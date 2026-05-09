from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class LLMResponse:
    content: str
    usage: TokenUsage = field(default_factory=TokenUsage)
    finish_reason: str = "stop"
    raw_response: dict[str, Any] | None = None


@dataclass
class ProviderConfig:
    provider: str  # deepseek | qwen | glm | moonshot | openai_compatible
    api_key: str
    base_url: str | None = None
    model: str | None = None
    extra_headers: dict[str, str] | None = None


class BaseLLMProvider(ABC):
    """LLM Provider 统一抽象基类，所有厂商必须实现此接口"""

    def __init__(self, config: ProviderConfig):
        self.config = config

    @abstractmethod
    async def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> LLMResponse:
        """发送对话请求，返回标准化 LLMResponse"""

    @abstractmethod
    def supports_tools(self) -> bool:
        """是否支持 Function Calling / Tools"""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Provider 唯一标识名"""
