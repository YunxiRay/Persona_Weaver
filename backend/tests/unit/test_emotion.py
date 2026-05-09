"""Unit tests for emotion/pacing module (tone analyzer)."""

from app.engine.empathy.emotion import EmotionAnalyzer, analyze_user_tone
from app.engine.empathy.pacing import PacingController


class TestAnalyzeUserTone:
    def test_refusal(self):
        result = analyze_user_tone("不想说！")
        assert result is not None
        assert "对抗" in result

    def test_refusal_plain(self):
        result = analyze_user_tone("不想说")
        assert result is not None
        assert "拒绝" in result

    def test_hesitation(self):
        result = analyze_user_tone("嗯……")
        assert result is not None
        assert "犹豫" in result

    def test_avoidance(self):
        result = analyze_user_tone("不知道")
        assert result is not None
        assert "模糊" in result

    def test_apathy(self):
        result = analyze_user_tone("随便")
        assert result is not None
        assert "冷漠" in result

    def test_anxiety(self):
        result = analyze_user_tone("好累")
        assert result is not None
        assert "耗竭" in result

    def test_end_intent(self):
        result = analyze_user_tone("结束")
        assert result is not None
        assert "终止" in result

    def test_very_short_input(self):
        result = analyze_user_tone("ab")
        assert result is not None
        assert "极简" in result

    def test_normal_input_returns_none(self):
        result = analyze_user_tone("我平时喜欢和朋友一起出去玩")
        assert result is None

    def test_empty_input(self):
        assert analyze_user_tone("") is None
        assert analyze_user_tone("   ") is None


class TestEmotionAnalyzer:
    def test_deflect_strategy_for_refusal(self):
        tone = analyze_user_tone("不想说")
        strategy = EmotionAnalyzer.get_strategy(tone)
        assert strategy == "DEFLECT"

    def test_soothe_strategy_for_anxiety(self):
        tone = analyze_user_tone("好累")
        strategy = EmotionAnalyzer.get_strategy(tone)
        assert strategy == "SOOTHE"

    def test_normal_strategy_for_none(self):
        strategy = EmotionAnalyzer.get_strategy(None)
        assert strategy == "NORMAL"


class TestPacingController:
    def test_initial_mode_is_normal(self):
        pc = PacingController()
        assert pc.mode == "NORMAL"
        assert not pc.should_ease_up

    def test_fatigue_builds_on_short_input(self):
        pc = PacingController()
        for _ in range(6):
            pc.on_user_input("ok")
        assert pc.should_ease_up

    def test_fatigue_decays_on_reply(self):
        pc = PacingController()
        for _ in range(10):
            pc.on_user_input("ok")
        for _ in range(20):
            pc.on_ai_reply()
        assert not pc.should_ease_up

    def test_light_mode_at_high_fatigue(self):
        pc = PacingController()
        for _ in range(10):
            pc.on_user_input("ok")
        assert pc.mode == "LIGHT"
