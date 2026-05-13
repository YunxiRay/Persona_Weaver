"""贝叶斯更新引擎 — 基于 Beta 分布的四维人格概率推理"""

import math

import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)

DIMENSIONS = ["E_I", "S_N", "T_F", "J_P"]

# Beta 先验参数 — 基于 MBTI 公开人口统计，总伪计数 = 4（弱先验）
# α/(α+β) 近似匹配 MBTI 人口比例
MBTI_PRIORS: dict[str, dict[str, float]] = {
    "E_I": {"alpha": 1.96, "beta": 2.04},   # E≈49%, I≈51%
    "S_N": {"alpha": 2.92, "beta": 1.08},   # S≈73%, N≈27%
    "T_F": {"alpha": 2.0,  "beta": 2.0},    # 平衡先验
    "J_P": {"alpha": 2.16, "beta": 1.84},   # J≈54%, P≈46%
}

OBSERVATION_WEIGHT = 1.0  # 每次 LLM 观测的伪计数权重基数
DECAY_RATE = 0.9  # 时间衰减系数：每轮对历史观测打 9 折，让近期对话权重更高


class DimensionTracker:
    """单个维度的 Beta 分布跟踪器"""

    def __init__(self, name: str):
        prior = MBTI_PRIORS[name]
        self.name = name
        self.alpha = prior["alpha"]
        self.beta = prior["beta"]
        self.sample_count: int = 0
        self.phase_samples: set[str] = set()  # 跨阶段样本来源

    @property
    def mean(self) -> float:
        return self.alpha / (self.alpha + self.beta)

    @property
    def std(self) -> float:
        total = self.alpha + self.beta
        if total == 0:
            return 1.0
        var = (self.alpha * self.beta) / (total * total * (total + 1))
        return math.sqrt(var)

    @property
    def is_converged(self) -> bool:
        return self.std < settings.INFERENCE_CONVERGENCE_THRESHOLD

    @property
    def cross_phase_count(self) -> int:
        return len(self.phase_samples)

    def update(self, observed_score: float, confidence: float, phase: str) -> None:
        """observed_score ∈ [-1, 1]（LLM 输出的维度值），confidence ∈ [0, 1]"""
        # ── 时间衰减：让历史观测权重指数级下降，防止早期印象锁死 ──
        if self.sample_count > 0:
            prior_alpha = MBTI_PRIORS[self.name]["alpha"]
            prior_beta = MBTI_PRIORS[self.name]["beta"]
            self.alpha = prior_alpha + (self.alpha - prior_alpha) * DECAY_RATE
            self.beta = prior_beta + (self.beta - prior_beta) * DECAY_RATE

        p = (observed_score + 1.0) / 2.0  # 映射到 [0, 1]
        p = max(0.01, min(0.99, p))       # 避免极端值导致退化
        weight = confidence * OBSERVATION_WEIGHT
        self.alpha += weight * p
        self.beta += weight * (1.0 - p)
        self.sample_count += 1
        self.phase_samples.add(phase)

    def dimension_score(self) -> float:
        """将后验均值映射回 [-1, 1]"""
        return self.mean * 2.0 - 1.0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "alpha": round(self.alpha, 3),
            "beta": round(self.beta, 3),
            "mean": round(self.mean, 4),
            "std": round(self.std, 4),
            "dimension_score": round(self.dimension_score(), 4),
            "converged": self.is_converged,
            "sample_count": self.sample_count,
            "cross_phase_count": self.cross_phase_count,
        }


class BayesianEngine:
    """四维贝叶斯推理引擎"""

    def __init__(self):
        self.trackers: dict[str, DimensionTracker] = {d: DimensionTracker(d) for d in DIMENSIONS}
        self.mbti_history: list[str] = []  # 最近 N 轮的 MBTI 类型序列

    def update(self, dimensions: dict[str, float], confidence: dict[str, float], phase: str) -> None:
        for dim in DIMENSIONS:
            score = dimensions.get(dim, 0.0)
            conf = confidence.get(dim, 0.5)
            self.trackers[dim].update(score, conf, phase)
        # 记录本轮 MBTI 类型
        self.mbti_history.append(self.determine_mbti())
        # 只保留最近 10 条
        if len(self.mbti_history) > 10:
            self.mbti_history = self.mbti_history[-10:]

    def is_converged(self) -> bool:
        """std 判据：所有维度后验标准差低于阈值"""
        return all(t.is_converged for t in self.trackers.values())

    def mbti_stable_for(self, rounds: int = 5) -> bool:
        """检查 MBTI 类型是否在过去 N 轮中保持不变"""
        if len(self.mbti_history) < rounds:
            return False
        recent = self.mbti_history[-rounds:]
        return len(set(recent)) == 1

    def dimension_scores(self) -> dict[str, float]:
        return {d: self.trackers[d].dimension_score() for d in DIMENSIONS}

    def confidence_values(self) -> dict[str, float]:
        return {d: round(1.0 - min(self.trackers[d].std * 3.0, 1.0), 4) for d in DIMENSIONS}

    def determine_mbti(self) -> str:
        scores = self.dimension_scores()
        mbti = ""
        mbti += "E" if scores["E_I"] > 0 else "I"
        mbti += "S" if scores["S_N"] > 0 else "N"
        mbti += "F" if scores["T_F"] > 0 else "T"  # T_F 正=Feeling, 负=Thinking
        mbti += "J" if scores["J_P"] > 0 else "P"
        return mbti

    def summary(self) -> dict:
        return {
            "mbti": self.determine_mbti(),
            "dimensions": {d: self.trackers[d].to_dict() for d in DIMENSIONS},
            "converged": self.is_converged(),
            "mbti_history": self.mbti_history,
        }
