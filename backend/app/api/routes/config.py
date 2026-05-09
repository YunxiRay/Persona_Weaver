from fastapi import APIRouter, HTTPException

from app.llm.provider import ProviderConfig
from app.llm.router import LLMRouter
from app.schemas.config import LLMConfigRequest, LLMConfigResponse, TestConnectionResponse

router = APIRouter(prefix="/config/llm", tags=["config"])

# In-memory store for LLM config (MVP: anonymous sessions)
# In production, anonymous config goes to Redis, registered config goes to PG
_config_store: dict[str, ProviderConfig] = {}


def _mask_key(key: str) -> str:
    if len(key) <= 4:
        return "****"
    return "****" + key[-4:]


@router.get("", response_model=LLMConfigResponse)
async def get_llm_config():
    """获取当前 LLM 配置（API Key 脱敏）"""
    cfg = _config_store.get("default")
    if not cfg:
        return LLMConfigResponse(provider="", api_key="", model="", base_url="", is_configured=False)
    return LLMConfigResponse(
        provider=cfg.provider,
        api_key=_mask_key(cfg.api_key),
        model=cfg.model or "",
        base_url=cfg.base_url or "",
        is_configured=True,
    )


@router.put("", response_model=LLMConfigResponse)
async def save_llm_config(body: LLMConfigRequest):
    """保存用户 LLM 配置"""
    if not body.api_key:
        raise HTTPException(status_code=400, detail="API Key 不能为空")
    if not body.provider:
        raise HTTPException(status_code=400, detail="Provider 不能为空")

    cfg = ProviderConfig(
        provider=body.provider,
        api_key=body.api_key,
        base_url=body.base_url if body.base_url else None,
        model=body.model if body.model else None,
    )
    _config_store["default"] = cfg
    return LLMConfigResponse(
        provider=cfg.provider,
        api_key=_mask_key(cfg.api_key),
        model=cfg.model or "",
        base_url=cfg.base_url or "",
        is_configured=True,
    )


@router.post("/test", response_model=TestConnectionResponse)
async def test_llm_connection(body: LLMConfigRequest):
    """发送一条简短测试消息验证连通性"""
    cfg = ProviderConfig(
        provider=body.provider,
        api_key=body.api_key,
        base_url=body.base_url if body.base_url else None,
        model=body.model if body.model else None,
    )
    router = LLMRouter(cfg)
    result = await router.test_connection()
    return TestConnectionResponse(**result)
