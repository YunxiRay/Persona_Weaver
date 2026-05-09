from app.llm.provider import BaseLLMProvider, ProviderConfig
from app.llm.providers.deepseek import DeepSeekProvider
from app.llm.providers.glm import GLMProvider
from app.llm.providers.moonshot import MoonshotProvider
from app.llm.providers.openai_compatible import OpenAICompatibleProvider
from app.llm.providers.qwen import QwenProvider

PROVIDER_MAP: dict[str, type[BaseLLMProvider]] = {
    "deepseek": DeepSeekProvider,
    "qwen": QwenProvider,
    "glm": GLMProvider,
    "moonshot": MoonshotProvider,
    "openai_compatible": OpenAICompatibleProvider,
}


def create_provider(config: ProviderConfig) -> BaseLLMProvider:
    if not config.api_key:
        raise ValueError(f"Provider '{config.provider}' 缺少 API Key，请在设置页配置")

    provider_cls = PROVIDER_MAP.get(config.provider)
    if provider_cls is None:
        supported = ", ".join(PROVIDER_MAP.keys())
        raise ValueError(f"不支持的 Provider '{config.provider}'，可选: {supported}")

    return provider_cls(config)
