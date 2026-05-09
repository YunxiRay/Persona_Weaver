from typing import Any

from openai import AsyncOpenAI

from app.llm.provider import BaseLLMProvider, LLMResponse, ProviderConfig, TokenUsage


class QwenProvider(BaseLLMProvider):
    DEFAULT_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    DEFAULT_MODEL = "qwen-plus"

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self._client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url or self.DEFAULT_BASE_URL,
        )

    @property
    def provider_name(self) -> str:
        return "qwen"

    def supports_tools(self) -> bool:
        return True

    async def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> LLMResponse:
        model = self.config.model or self.DEFAULT_MODEL
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 2048)
        response_format = kwargs.get("response_format", None)

        params: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
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
