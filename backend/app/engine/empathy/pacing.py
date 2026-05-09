"""节奏控制模块 — 监测用户回复速度和输入量，动态调整对话节奏"""

import time

import structlog

logger = structlog.get_logger(__name__)


class PacingController:
    """对话节奏控制器：监测用户疲劳，自动切换轻松模式"""

    def __init__(self, idle_threshold_seconds: float = 60.0, short_input_threshold: int = 10):
        self.idle_threshold = idle_threshold_seconds
        self.short_input_threshold = short_input_threshold
        self.last_input_time: float | None = None
        self.last_input_length: int = 0
        self.fatigue_score: float = 0.0

    def on_user_input(self, input_text: str) -> None:
        now = time.time()
        if self.last_input_time is not None:
            gap = now - self.last_input_time
            if gap > self.idle_threshold:
                self.fatigue_score += 0.3
                logger.info("user_idle_detected", gap_seconds=round(gap, 1))
        self.last_input_time = now
        self.last_input_length = len(input_text.strip())

        if self.last_input_length < self.short_input_threshold:
            self.fatigue_score += 0.1

        self.fatigue_score = min(self.fatigue_score, 1.0)

    def on_ai_reply(self) -> None:
        self.fatigue_score = max(self.fatigue_score - 0.05, 0.0)

    @property
    def should_ease_up(self) -> bool:
        return self.fatigue_score > 0.5

    @property
    def mode(self) -> str:
        if self.fatigue_score > 0.7:
            return "LIGHT"       # 故事共创模式，最轻松
        if self.fatigue_score > 0.5:
            return "RELAXED"     # 轻松模式
        return "NORMAL"
