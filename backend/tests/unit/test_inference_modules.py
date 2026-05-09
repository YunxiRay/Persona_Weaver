"""Unit tests for validator, semantic, and defense modules."""

from app.engine.inference.bayesian import BayesianEngine
from app.engine.inference.defense import DefenseDetector
from app.engine.inference.semantic import (
    analyze_abstract_concrete_ratio,
    compute_sn_aux_signal,
    extract_keywords,
)
from app.engine.inference.validator import InferenceValidator


class TestValidator:
    def test_insufficient_samples(self):
        engine = BayesianEngine()
        engine.update({"E_I": 0.5, "S_N": 0.0, "T_F": 0.0, "J_P": 0.0},
                      {"E_I": 0.5, "S_N": 0.3, "T_F": 0.2, "J_P": 0.4},
                      "RAPPORT")
        v = InferenceValidator(engine)
        result = v.validate()
        assert not result["valid"]
        assert "confidence_limited" in str(result["flags"])

    def test_validated_after_enough_samples(self):
        engine = BayesianEngine()
        for _ in range(6):
            engine.update({"E_I": 0.5, "S_N": 0.0, "T_F": 0.0, "J_P": 0.0},
                          {"E_I": 0.5, "S_N": 0.3, "T_F": 0.2, "J_P": 0.4},
                          "EXPLORATION")
        v = InferenceValidator(engine)
        result = v.validate()
        assert result["total_samples"] == 24  # 6 updates * 4 dimensions


class TestSemanticKeywords:
    def test_extract_keywords(self):
        msgs = [
            "我喜欢和朋友一起去旅行，看不同的风景",
            "旅行能让我放松心情，特别是一个人去海边的时候",
        ]
        keywords = extract_keywords(msgs, top_n=5)
        assert len(keywords) > 0
        # "旅行" should be a top keyword
        words = [k[0] for k in keywords]
        assert "旅行" in words

    def test_empty_input(self):
        result = extract_keywords([], top_n=5)
        assert result == []


class TestAbstractConcrete:
    def test_abstract_text(self):
        text = "自由和幸福是人生的终极意义，我们在追求内心的平静与灵魂的永恒"
        result = analyze_abstract_concrete_ratio(text)
        assert result["abstract_count"] > 0

    def test_concrete_text(self):
        text = "我早上喝了咖啡吃了面包，然后坐地铁去公司上班"
        result = analyze_abstract_concrete_ratio(text)
        assert result["concrete_count"] > 0

    def test_empty_text(self):
        result = analyze_abstract_concrete_ratio("")
        assert result["abstract_ratio"] == 0.5

    def test_sn_aux_signal_abstract(self):
        signal = compute_sn_aux_signal(0.8)
        assert signal > 0  # abstract → N (intuitive)

    def test_sn_aux_signal_concrete(self):
        signal = compute_sn_aux_signal(0.2)
        assert signal < 0  # concrete → S (sensing)


class TestDefenseDetector:
    def test_normal_input(self):
        d = DefenseDetector()
        result = d.analyze("我喜欢和朋友一起出去玩，周末经常去爬山")
        assert result["flags"] == []

    def test_idealization_detection(self):
        d = DefenseDetector()
        result = d.analyze("他真的太完美了，超级棒，是我见过最棒的人")
        assert "idealization" in result["flags"]

    def test_devaluation_detection(self):
        d = DefenseDetector()
        result = d.analyze("这个垃圾公司，真的太差了，糟透了")
        assert "devaluation" in result["flags"]

    def test_avoidance_pattern(self):
        d = DefenseDetector()
        for _ in range(3):
            result = d.analyze("嗯", "你觉得为什么会这样呢？")
        assert "avoidance_pattern" in result["flags"]

    def test_avoidance_resets(self):
        d = DefenseDetector()
        d.analyze("嗯", "你觉得工作压力大吗？")
        d.analyze("哦", "压力主要来自哪里？")
        # Third response is relevant, shares keywords with guide
        result = d.analyze("压力主要来自工作太多", "你觉得压力大吗？")
        assert "avoidance_pattern" not in result["flags"]

    def test_invalid_info_rate(self):
        d = DefenseDetector()
        result = d.analyze("嗯", "你觉得为什么会这样呢？")
        assert result["relevance"] < 0.5
        assert result["invalid_info_rate"] > 0.5
