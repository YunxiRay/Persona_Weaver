"""阶段状态机 — 控制对话四阶段递进，根据置信度和轮次自动跃迁"""

import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)

PHASES = ["RAPPORT", "EXPLORATION", "CONFRONTATION", "SYNTHESIS", "ENDED"]

MIN_TURNS_PER_PHASE: dict[str, int] = {
    "RAPPORT": 3,
    "EXPLORATION": 5,
    "CONFRONTATION": 4,
    "SYNTHESIS": 2,
}

CONFIDENCE_THRESHOLD = 0.70
CONVERGENCE_THRESHOLD = settings.INFERENCE_CONVERGENCE_THRESHOLD  # 0.08

PHASE_LABELS: dict[str, str] = {
    "RAPPORT": "正在建立连接...",
    "EXPLORATION": "正在深入探索...",
    "CONFRONTATION": "正在触及核心...",
    "SYNTHESIS": "正在整理画像...",
    "ENDED": "对话已结束",
}


class Conductor:
    """叙事引导状态机"""

    def __init__(
        self,
        current_phase: str = "RAPPORT",
        turn_count: int = 0,
        effective_words: int = 0,
    ):
        self.current_phase = current_phase
        self.turn_count = turn_count
        self.effective_words = effective_words

    def evaluate_transition(
        self,
        confidence: dict[str, float],
        risk_level: str = "LOW",
    ) -> str:
        """评估是否跃迁到下一阶段，返回新阶段名"""
        if self.current_phase == "ENDED":
            return "ENDED"

        if risk_level == "HIGH":
            logger.warning("safety_anchor_triggered", phase=self.current_phase)
            if self.current_phase != "RAPPORT":
                return self._retreat_to_safe_phase()
            return "RAPPORT"

        min_turns = MIN_TURNS_PER_PHASE.get(self.current_phase, 3)
        if self.turn_count < min_turns:
            return self.current_phase

        if self._should_skip_to_synthesis(confidence):
            logger.info("early_convergence", effective_words=self.effective_words)
            return "SYNTHESIS"

        if self.current_phase == "RAPPORT" and self.effective_words >= 200:
            return "EXPLORATION"
        if self.current_phase == "EXPLORATION" and self.effective_words >= 500:
            return "CONFRONTATION"
        if self.current_phase == "CONFRONTATION" and self._all_confident(confidence):
            return "SYNTHESIS"
        if self.current_phase == "SYNTHESIS":
            return "ENDED"

        return self.current_phase

    def advance(self, new_effective_words: int) -> None:
        self.turn_count += 1
        self.effective_words += new_effective_words

    def set_phase(self, phase: str) -> None:
        if phase in PHASES:
            self.current_phase = phase

    def is_converged(self, confidence: dict[str, float]) -> bool:
        return self._all_confident(confidence)

    def _should_skip_to_synthesis(self, confidence: dict[str, float]) -> bool:
        """若在早期阶段四维置信度均已极高 + 有效字数充足 + 最小轮次满足，可跳过对峙期"""
        if self.current_phase not in ("RAPPORT", "EXPLORATION"):
            return False
        # 最小探索轮次保底：即使置信度达标，也必须至少聊满 10 轮
        if self.turn_count < 10:
            return False
        return self._all_confident(confidence) and self.effective_words >= 600

    def _all_confident(self, confidence: dict[str, float]) -> bool:
        dims = ["E_I", "S_N", "T_F", "J_P"]
        return all(confidence.get(d, 0.0) >= CONFIDENCE_THRESHOLD for d in dims)

    def _retreat_to_safe_phase(self) -> str:
        idx = PHASES.index(self.current_phase)
        return PHASES[max(0, idx - 1)]

    def to_dict(self) -> dict:
        return {
            "phase": self.current_phase,
            "turn_count": self.turn_count,
            "effective_words": self.effective_words,
        }

    @staticmethod
    def from_dict(data: dict) -> "Conductor":
        return Conductor(
            current_phase=data.get("phase", "RAPPORT"),
            turn_count=data.get("turn_count", 0),
            effective_words=data.get("effective_words", 0),
        )
