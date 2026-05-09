from pydantic import BaseModel


class WSMessageIn(BaseModel):
    """前端通过 WebSocket 发送的消息"""
    type: str = "message"  # message | ping | config
    content: str = ""      # 用户输入文本
    provider: str = ""     # LLM provider
    api_key: str = ""      # 用户 API Key
    model: str = ""        # 模型名
    base_url: str = ""     # Base URL


class WSMessageOut(BaseModel):
    """后端通过 WebSocket 返回的消息"""
    type: str                    # reply | phase_change | error | pong | safety_alert
    content: str = ""            # AI 回复文本
    phase: str = ""              # 当前阶段
    phase_label: str = ""        # 阶段中文标签
    is_final: bool = False       # 是否最终回复（触发报告生成）
    session_id: str = ""         # 会话 ID
    turn: int = 0                # 当前轮次
    error: str = ""              # 错误信息


PHASE_LABELS: dict[str, str] = {
    "RAPPORT": "正在建立连接...",
    "EXPLORATION": "正在深入探索...",
    "CONFRONTATION": "正在触及核心...",
    "SYNTHESIS": "正在整理画像...",
    "ENDED": "对话已结束",
}
