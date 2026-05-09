import structlog

from app.llm.provider import BaseLLMProvider, ProviderConfig
from app.llm.provider_factory import create_provider

logger = structlog.get_logger(__name__)


class LLMRouter:
    """会话级 LLM Provider 路由：每个会话创建时构建 Provider 实例，整个会话复用"""

    def __init__(self, config: ProviderConfig):
        self.config = config
        self._provider: BaseLLMProvider | None = None

    @property
    def provider(self) -> BaseLLMProvider:
        if self._provider is None:
            self._provider = create_provider(self.config)
            logger.info("provider_initialized", provider=self._provider.provider_name)
        return self._provider

    @classmethod
    def from_dict(cls, data: dict) -> "LLMRouter":
        config = ProviderConfig(
            provider=data.get("provider", "deepseek"),
            api_key=data.get("api_key", ""),
            base_url=data.get("base_url"),
            model=data.get("model"),
            extra_headers=data.get("extra_headers"),
        )
        return cls(config)

    async def test_connection(self) -> dict:
        """发送简短测试消息验证连通性"""
        try:
            resp = await self.provider.chat(
                messages=[{"role": "user", "content": "Hello, respond with just 'OK'."}],
                max_tokens=10,
                temperature=0.0,
            )
            return {"success": True, "provider": self.provider.provider_name, "latency_ms": 0}
        except Exception as e:
            logger.warning("provider_test_failed", error=str(e))
            return {"success": False, "provider": self.config.provider, "error": str(e)}
