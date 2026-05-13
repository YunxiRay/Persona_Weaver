"""防御机制检测 — 无效信息率 / 回避特征 / 理想化/贬低检测"""

import re

import structlog

logger = structlog.get_logger(__name__)

# 极端正面情感词
EXTREME_POSITIVE: set[str] = {
    "完美", "最好", "超级", "无敌", "绝对", "无与伦比", "最棒", "一级棒",
    "太棒了", "太好了", "非常好", "棒极了", "绝了", "顶级", "神", "神仙",
    "完美无缺", "十全十美", "无懈可击", "无暇", "完美至极",
}

# 极端负面情感词
EXTREME_NEGATIVE: set[str] = {
    "垃圾", "最差", "恶心", "讨厌", "烂", "糟透了", "恶心死了", "废物",
    "一无是处", "毫无价值", "死了算了", "糟糕透顶", "烦死了", "恨死了",
    "绝望", "崩溃", "完蛋", "没救了", "太差了", "差劲", "劣质",
}

# 引导问题关键词（用于检测用户是否在回应引导）
GUIDE_QUESTION_KEYWORDS: set[str] = {
    "为什么", "怎么样", "如何", "什么", "哪里", "怎么", "描述", "你觉得",
    "你如何", "你认为", "分享", "告诉我", "聊一聊", "说说", "你怎么看",
}


class DefenseDetector:
    """防御机制检测器"""

    def __init__(self):
        self.consecutive_avoid_count = 0
        self.total_input_chars = 0
        self.relevant_chars = 0

    def analyze(self, user_input: str, last_ai_question: str = "") -> dict:
        """分析单轮输入的防御特征"""
        flags: list[str] = []
        input_clean = user_input.strip()
        total_chars = len(input_clean.replace(" ", ""))

        self.total_input_chars += total_chars

        # 1. 回应相关性检测
        relevance = self._check_relevance(user_input, last_ai_question)

        # 追踪相关字符数（修复 relevant_chars 永不为0的bug）
        if relevance > 0.3:
            self.relevant_chars += total_chars

        # 2. 无效信息率
        if total_chars > 0:
            invalid_rate = 1.0 - relevance
        else:
            invalid_rate = 1.0

        # 3. 回避特征：连续 3 轮未正面回应
        if relevance <= 0.3:
            self.consecutive_avoid_count += 1
        else:
            self.consecutive_avoid_count = 0

        if self.consecutive_avoid_count >= 3:
            flags.append("avoidance_pattern")
            logger.info("avoidance_pattern_detected", consecutive=self.consecutive_avoid_count)

        # 4. 理想化/贬低检测
        positive_hits = [w for w in EXTREME_POSITIVE if w in input_clean]
        negative_hits = [w for w in EXTREME_NEGATIVE if w in input_clean]
        if len(positive_hits) >= 2:
            flags.append("idealization")
        if len(negative_hits) >= 2:
            flags.append("devaluation")
        if len(positive_hits) + len(negative_hits) >= 3:
            flags.append("splitting")

        # 5. 信息密度
        info_density = relevance if total_chars > 0 else 0.0

        overall_invalid_rate = 1.0 - (self.relevant_chars / max(self.total_input_chars, 1))

        result = {
            "invalid_info_rate": round(invalid_rate, 3),
            "overall_invalid_rate": round(overall_invalid_rate, 3),
            "relevance": round(relevance, 3),
            "consecutive_avoid": self.consecutive_avoid_count,
            "flags": flags,
            "info_density": round(info_density, 3),
        }

        if flags:
            logger.info("defense_flags", flags=flags, relevance=round(relevance, 3))

        return result

    def _check_relevance(self, user_input: str, ai_question: str) -> float:
        """简单关键词重叠法：检查用户输入是否包含与引导问题相关的词汇"""
        if not ai_question:
            return 0.5

        # 从 AI 引导问题中提取主题词
        guide_words = set(jieba_lcut_keywords(ai_question))
        user_words = set(jieba_lcut_keywords(user_input))

        if not guide_words:
            return 0.5

        overlap = guide_words & user_words
        # 考虑用户输入长度：太短可能有其他原因
        if len(user_input.strip()) < 5:
            return 0.3  # 太短通常不够相关

        return min(1.0, len(overlap) / max(len(guide_words), 1) * 1.5)

    def from_llm_flags(self, llm_flags: list[str]) -> dict:
        """优先使用 LLM 返回的 defense_flags，仅合并持续回避检测"""
        flags = [f for f in llm_flags if f in ("avoidance", "idealization", "devaluation", "splitting")]
        if self.consecutive_avoid_count >= 3 and "avoidance" not in flags:
            flags.append("avoidance_pattern")
        return {"flags": flags, "source": "llm" if llm_flags else "keyword"}

    def reset(self) -> None:
        self.consecutive_avoid_count = 0
        self.total_input_chars = 0
        self.relevant_chars = 0


def jieba_lcut_keywords(text: str) -> set[str]:
    """使用 jieba 提取主题关键词"""
    import jieba
    from app.engine.inference.semantic import STOP_WORDS

    words = jieba.lcut(text)
    return {w.strip() for w in words if len(w.strip()) >= 2 and w.strip() not in STOP_WORDS}
