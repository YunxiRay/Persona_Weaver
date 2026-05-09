"""多点校验器 — 确保单维度判定基于 ≥5 个跨阶段语料片段"""

import structlog

from app.engine.inference.bayesian import DIMENSIONS, BayesianEngine

logger = structlog.get_logger(__name__)

MIN_CROSS_PHASE_SAMPLES = 5


class InferenceValidator:
    """推理结果校验器"""

    def __init__(self, engine: BayesianEngine):
        self.engine = engine
        self.warnings: list[str] = []

    def validate(self) -> dict:
        self.warnings = []
        flags: dict[str, str] = {}

        for dim in DIMENSIONS:
            tracker = self.engine.trackers[dim]
            if tracker.sample_count < MIN_CROSS_PHASE_SAMPLES:
                msg = f"{dim} 维度样本不足（{tracker.sample_count} < {MIN_CROSS_PHASE_SAMPLES}），置信度受限"
                self.warnings.append(msg)
                flags[dim] = "confidence_limited"
            elif tracker.cross_phase_count < 2:
                msg = f"{dim} 维度缺乏跨阶段验证（仅 {tracker.cross_phase_count} 个阶段），建议补充语料"
                self.warnings.append(msg)
                flags[dim] = "single_phase_only"
            else:
                flags[dim] = "validated"

        if self.warnings:
            logger.info("validation_warnings", count=len(self.warnings), warnings=self.warnings)

        return {
            "valid": len(self.warnings) == 0,
            "flags": flags,
            "warnings": self.warnings,
            "total_samples": sum(self.engine.trackers[d].sample_count for d in DIMENSIONS),
        }
