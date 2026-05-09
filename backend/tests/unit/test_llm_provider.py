"""Unit tests for LLM provider base classes and factory."""

import pytest

from app.llm.provider import LLMResponse, ProviderConfig, TokenUsage
from app.llm.provider_factory import create_provider
from app.llm.providers.deepseek import DeepSeekProvider
from app.llm.providers.glm import GLMProvider
from app.llm.providers.moonshot import MoonshotProvider
from app.llm.providers.openai_compatible import OpenAICompatibleProvider
from app.llm.providers.qwen import QwenProvider


class TestProviderConfig:
    def test_minimal_config(self):
        cfg = ProviderConfig(provider="deepseek", api_key="sk-test")
        assert cfg.provider == "deepseek"
        assert cfg.api_key == "sk-test"
        assert cfg.base_url is None

    def test_full_config(self):
        cfg = ProviderConfig(
            provider="openai_compatible",
            api_key="sk-test",
            base_url="http://localhost:11434/v1",
            model="llama3",
        )
        assert cfg.model == "llama3"
        assert cfg.base_url == "http://localhost:11434/v1"


class TestTokenUsage:
    def test_defaults(self):
        usage = TokenUsage()
        assert usage.prompt_tokens == 0
        assert usage.completion_tokens == 0

    def test_with_values(self):
        usage = TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
        assert usage.total_tokens == 150


class TestLLMResponse:
    def test_basic_response(self):
        resp = LLMResponse(content="Hello")
        assert resp.content == "Hello"
        assert resp.finish_reason == "stop"


class TestProviderFactory:
    def test_create_deepseek(self):
        cfg = ProviderConfig(provider="deepseek", api_key="sk-test")
        p = create_provider(cfg)
        assert isinstance(p, DeepSeekProvider)
        assert p.provider_name == "deepseek"

    def test_create_qwen(self):
        cfg = ProviderConfig(provider="qwen", api_key="sk-test")
        p = create_provider(cfg)
        assert isinstance(p, QwenProvider)

    def test_create_glm(self):
        cfg = ProviderConfig(provider="glm", api_key="sk-test")
        p = create_provider(cfg)
        assert isinstance(p, GLMProvider)

    def test_create_moonshot(self):
        cfg = ProviderConfig(provider="moonshot", api_key="sk-test")
        p = create_provider(cfg)
        assert isinstance(p, MoonshotProvider)

    def test_create_openai_compatible(self):
        cfg = ProviderConfig(
            provider="openai_compatible",
            api_key="sk-test",
            base_url="http://localhost:11434/v1",
            model="llama3",
        )
        p = create_provider(cfg)
        assert isinstance(p, OpenAICompatibleProvider)

    def test_missing_api_key_raises(self):
        cfg = ProviderConfig(provider="deepseek", api_key="")
        with pytest.raises(ValueError, match="缺少 API Key"):
            create_provider(cfg)

    def test_unknown_provider_raises(self):
        cfg = ProviderConfig(provider="unknown", api_key="sk-test")
        with pytest.raises(ValueError, match="不支持的 Provider"):
            create_provider(cfg)

    def test_openai_compatible_requires_base_url(self):
        cfg = ProviderConfig(provider="openai_compatible", api_key="sk-test")
        with pytest.raises(ValueError, match="base_url"):
            create_provider(cfg)
