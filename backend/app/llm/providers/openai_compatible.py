from typing import Any

from openai import AsyncOpenAI

from app.llm.provider import BaseLLMProvider, LLMResponse, ProviderConfig, TokenUsage


class OpenAICompatibleProvider(BaseLLMProvider):
    """通用 OpenAI 兼容 Provider：支持 Ollama / vLLM / LocalAI / 任意兼容接口"""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        if not config.base_url:
            raise ValueError("OpenAI 兼容 Provider 必须提供 base_url")
        if not config.model:
            raise ValueError("OpenAI 兼容 Provider 必须提供 model")
        self._client = AsyncOpenAI(
            api_key=config.api_key or "not-needed",
            base_url=config.base_url,
        )

    @property
    def provider_name(self) -> str:
        return "openai_compatible"

    def supports_tools(self) -> bool:
        return True

    async def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> LLMResponse:
        model = self.config.model or ""
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 2048)
        response_format = kwargs.get("response_format", None)

        extra_headers = self.config.extra_headers or {}
        params: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "extra_headers": extra_headers,
        }
        if response_format:
            params["response_format"] = response_format

        resp = await self._client.chat.completions.create(**params)

        choice = resp.choices[0]
        return LLMResponse(
            content=choice.message.content or "",
            usage=TokenUsage(
                prompt_tokens=resp.usage.prompt_tokens if resp.usage else 0,
                completion_tokens=resp.usage.completion_tokens if resp.usage else 0,
                total_tokens=resp.usage.total_tokens if resp.usage else 0,
            ),
            finish_reason=choice.finish_reason or "stop",
            raw_response=resp.model_dump(),
        )
