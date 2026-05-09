from fastapi import HTTPException


class ProviderError(HTTPException):
    """LLM Provider 统一错误"""

    @classmethod
    def invalid_key(cls, provider: str) -> "ProviderError":
        return cls(status_code=401, detail=f"API Key 无效，请检查 {provider} 的设置")

    @classmethod
    def insufficient_balance(cls) -> "ProviderError":
        return cls(status_code=402, detail="账户余额不足，请充值后重试")

    @classmethod
    def timeout(cls) -> "ProviderError":
        return cls(status_code=503, detail="LLM 请求超时，请检查网络或切换 Provider")

    @classmethod
    def network_error(cls) -> "ProviderError":
        return cls(status_code=503, detail="网络错误，请检查网络连接或切换 Provider")

    @classmethod
    def not_configured(cls) -> "ProviderError":
        return cls(status_code=400, detail="尚未配置 LLM Provider，请先在设置页配置 API Key")
