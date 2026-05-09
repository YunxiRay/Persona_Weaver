"""Unit tests for report generator (without real LLM calls)."""

import pytest

from app.engine.inference.bayesian import BayesianEngine
from app.services.report_generator import PERSONALITY_LABELS, SBTI_GUIDES, ReportGenerator


class TestReportGenerator:
    @pytest.fixture
    def engine(self):
        e = BayesianEngine()
        # Simulate many updates so we get a stable MBTI
        for _ in range(15):
            e.update(
                {"E_I": 0.5, "S_N": -0.4, "T_F": 0.6, "J_P": 0.3},
                {"E_I": 0.8, "S_N": 0.8, "T_F": 0.8, "J_P": 0.8},
                "CONFRONTATION",
            )
        return e

    def test_build_skeleton(self, engine):
        gen = ReportGenerator()
        skeleton = gen.build_skeleton(engine)
        assert skeleton.mbti_type in PERSONALITY_LABELS
        assert -1.0 <= skeleton.dimension_scores.E_I <= 1.0
        assert -1.0 <= skeleton.dimension_scores.S_N <= 1.0
        assert -1.0 <= skeleton.dimension_scores.T_F <= 1.0
        assert -1.0 <= skeleton.dimension_scores.J_P <= 1.0

    def test_build_cognitive_map(self, engine):
        gen = ReportGenerator()
        cmap = gen.build_cognitive_map(engine)
        assert hasattr(cmap, "work")
        assert hasattr(cmap, "relationship")
        assert hasattr(cmap, "crisis")

    def test_build_linguistic_sketch(self):
        gen = ReportGenerator()
        msgs = [
            "我经常思考人生的意义和自由的价值",
            "抽象概念对我来说很有吸引力",
            "我喜欢探讨哲学问题",
        ]
        sketch = gen.build_linguistic_sketch(msgs)
        assert len(sketch.style_label) > 0
        assert len(sketch.top_keywords) >= 0
        assert 0.0 <= sketch.abstract_ratio <= 1.0

    def test_build_linguistic_sketch_concrete(self):
        gen = ReportGenerator()
        msgs = [
            "我早上喝了咖啡吃了面包坐地铁去公司",
            "办公室的电脑键盘需要换新的了",
            "昨天去超市买了牛奶和水果",
        ]
        sketch = gen.build_linguistic_sketch(msgs)
        assert sketch.concrete_ratio > 0

    def test_build_sbti_label_known_type(self):
        gen = ReportGenerator()
        label = gen.build_sbti_label("INTJ")
        assert "建筑师" in label.social_survival_guide or "社交" in label.social_survival_guide
        assert "灵魂合拍" in label.soul_match_index

    def test_build_sbti_label_unknown_type(self):
        gen = ReportGenerator()
        label = gen.build_sbti_label("XXXX")
        assert len(label.social_survival_guide) > 0

    def test_default_therapist_note(self):
        gen = ReportGenerator()
        note = gen._default_therapist_note("INTJ")
        assert "INTJ" in note
        assert len(note) > 50

    @pytest.mark.asyncio
    async def test_generate_without_provider(self, engine):
        gen = ReportGenerator()  # No provider
        result = await gen.generate(
            engine=engine,
            all_messages=["测试消息1", "测试消息2"],
            history=[{"role": "user", "content": "你好"}],
        )
        assert "personality_skeleton" in result
        assert "cognitive_map" in result
        assert "linguistic_sketch" in result
        assert "sbti_label" in result
        assert "therapist_note" in result
        assert len(result["personality_skeleton"]["mbti_type"]) == 4


class TestSBTIGuides:
    def test_all_16_types_have_guides(self):
        all_types = [
            "INTJ", "INTP", "ENTJ", "ENTP",
            "INFJ", "INFP", "ENFJ", "ENFP",
            "ISTJ", "ISFJ", "ESTJ", "ESFJ",
            "ISTP", "ISFP", "ESTP", "ESFP",
        ]
        for t in all_types:
            assert t in SBTI_GUIDES, f"Missing SBTI guide for {t}"
            assert t in PERSONALITY_LABELS, f"Missing label for {t}"
