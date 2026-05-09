import json

import structlog
from fastapi import WebSocket, WebSocketDisconnect

from app.core.security import check_rate_limit, sanitize_input, detect_crisis, validate_user_input
from app.engine.chat_pipeline import run_pipeline
from app.llm.provider import ProviderConfig

logger = structlog.get_logger(__name__)


async def chat_websocket(ws: WebSocket) -> None:
    await ws.accept()
    session_id: str | None = None
    provider_cfg: ProviderConfig | None = None
    client_ip = ws.client.host if ws.client else "unknown"

    try:
        while True:
            raw = await ws.receive_text()

            # Rate limit check (20 req/min per IP for WebSocket messages)
            if not check_rate_limit(f"ws:{client_ip}", max_requests=30, window=60):
                await ws.send_json({"type": "error", "error": "请求过于频繁，请稍后再试"})
                continue

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
                raw_input = data.get("content", "").strip()

                if not raw_input:
                    await ws.send_json({"type": "error", "error": "输入不能为空"})
                    continue

                # Sanitize input
                user_input = sanitize_input(raw_input)

                # Validate input quality
                validation_error = validate_user_input(user_input)
                if validation_error:
                    await ws.send_json({"type": "error", "error": validation_error})
                    continue

                # Crisis detection
                crisis = detect_crisis(user_input)
                if crisis["risk_level"] == "HIGH":
                    await ws.send_json({
                        "type": "safety_alert",
                        "content": (
                            f"我注意到你的一些表达让我有些担心。作为 AI，我无法提供专业的心理危机干预，"
                            f"但请记住你并不孤单。如果你正在经历困难，请拨打心理援助热线：{crisis['helpline']}。"
                            f"我们可以继续对话，但请优先照顾好自己的安全。"
                        ),
                        "helpline": crisis["helpline"],
                    })
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

                try:
                    result = await run_pipeline(
                        user_input=user_input,
                        session_id=session_id,
                        provider_cfg=provider_cfg,
                    )
                except Exception as pipeline_err:
                    logger.error("pipeline_error", error=str(pipeline_err))
                    await ws.send_json({
                        "type": "error",
                        "error": "处理消息时发生错误，请重试",
                    })
                    continue

                if "session_id" in result:
                    session_id = result["session_id"]

                await ws.send_json(result)

    except WebSocketDisconnect:
        logger.info("websocket_disconnected", session_id=session_id)
        # Session state remains in memory for reconnection
    except Exception as e:
        logger.error("websocket_error", error=str(e))
        try:
            await ws.send_json({"type": "error", "error": "服务器内部错误，请刷新页面重试"})
        except Exception:
            pass
