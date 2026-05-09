import json

import structlog
from fastapi import WebSocket, WebSocketDisconnect

from app.engine.chat_pipeline import run_pipeline
from app.llm.provider import ProviderConfig

logger = structlog.get_logger(__name__)


async def chat_websocket(ws: WebSocket) -> None:
    await ws.accept()
    session_id: str | None = None
    provider_cfg: ProviderConfig | None = None

    try:
        while True:
            raw = await ws.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await ws.send_json({"type": "error", "error": "无效的 JSON 格式"})
                continue

            msg_type = data.get("type", "")
            if msg_type == "ping":
                await ws.send_json({"type": "pong"})
                continue

            if msg_type == "config":
                provider_cfg = ProviderConfig(
                    provider=data.get("provider", "deepseek"),
                    api_key=data.get("api_key", ""),
                    base_url=data.get("base_url") or None,
                    model=data.get("model") or None,
                )
                await ws.send_json({"type": "config_ack", "provider": provider_cfg.provider})
                continue

            if msg_type in ("message", ""):
                user_input = data.get("content", "").strip()
                if not user_input:
                    await ws.send_json({"type": "error", "error": "输入不能为空"})
                    continue

                if provider_cfg is None:
                    if not data.get("api_key"):
                        await ws.send_json({"type": "error", "error": "请先配置 LLM API Key，访问 /settings 设置"})
                        continue
                    provider_cfg = ProviderConfig(
                        provider=data.get("provider", "deepseek"),
                        api_key=data.get("api_key", ""),
                        base_url=data.get("base_url") or None,
                        model=data.get("model") or None,
                    )

                session_id = data.get("session_id") or session_id

                result = await run_pipeline(
                    user_input=user_input,
                    session_id=session_id,
                    provider_cfg=provider_cfg,
                )

                if "session_id" in result:
                    session_id = result["session_id"]

                await ws.send_json(result)

    except WebSocketDisconnect:
        logger.info("websocket_disconnected", session_id=session_id)
    except Exception as e:
        logger.error("websocket_error", error=str(e))
        try:
            await ws.send_json({"type": "error", "error": "服务器内部错误"})
        except Exception:
            pass
