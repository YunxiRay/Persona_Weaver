"""Edge case and resilience tests for Phase 8 — security, input, and error handling."""

import time
import pytest

from app.core.security import (
    sanitize_input,
    validate_user_input,
    detect_crisis,
    create_session_token,
    validate_session_token,
    check_rate_limit,
    should_purge_session,
)


class TestInputEdgeCases:
    def test_empty_string(self):
        assert sanitize_input("") == ""

    def test_only_whitespace(self):
        assert sanitize_input("   \t\n  ") == "   \t\n  "

    def test_mixed_chinese_english_numbers(self):
        result = sanitize_input("我今年25岁，from北京，email是test@example.com")
        assert result == "我今年25岁，from北京，email是test@example.com"

    def test_special_chinese_punctuation(self):
        text = "今天心情很好！你呢？我觉得……"
        assert sanitize_input(text) == text

    def test_partial_xss_gibberish(self):
        text = "on<br>error handler test"
        result = sanitize_input(text)
        assert "[filtered]" not in result  # partial fragment shouldn't trigger

    def test_null_bytes(self):
        text = "hello\x00world"
        result = sanitize_input(text)
        assert len(result) > 0

    def test_very_short_valid_chinese(self):
        assert validate_user_input("你好") is None

    def test_mixed_valid_short(self):
        assert validate_user_input("嗯，好的") is None


class TestRateLimitEdgeCases:
    def test_single_request_always_allowed(self):
        assert check_rate_limit(f"single_{time.time()}", max_requests=20, window=60)

    def test_exact_boundary(self):
        ident = f"boundary_{time.time()}"
        for _ in range(19):
            assert check_rate_limit(ident, max_requests=20, window=60)
        # 20th request — should pass
        assert check_rate_limit(ident, max_requests=20, window=60)
        # 21st — should fail
        assert not check_rate_limit(ident, max_requests=20, window=60)

    def test_different_windows_different_limits(self):
        ident = f"win_{time.time()}"
        results = [check_rate_limit(ident, max_requests=5, window=3600) for _ in range(10)]
        assert sum(results) == 5  # exactly 5 allowed


class TestCrisisEdgeCases:
    def test_keyword_partial_match(self):
        # "自杀" embedded in other words should still trigger
        result = detect_crisis("我想自杀吗？不是的")
        assert result["risk_level"] == "HIGH"

    def test_multiple_keywords(self):
        result = detect_crisis("我感觉很痛苦想自杀自残")
        assert result["risk_level"] == "HIGH"
        assert len(result["trigger_keywords"]) >= 2

    def test_case_insensitive(self):
        # Keywords are exact Chinese characters, but test mixed content
        result = detect_crisis("I want to 伤害自己 today")
        assert result["risk_level"] == "HIGH"

    def test_no_false_positive(self):
        result = detect_crisis("今天跟朋友吵架了，心情不太好")
        assert result["risk_level"] == "LOW"


class TestSessionEdgeCases:
    def test_token_validation_after_creation(self):
        token = create_session_token()
        assert validate_session_token(token)
        # Second validation should also work
        assert validate_session_token(token)

    def test_purge_boundary_seconds(self):
        now = time.time()
        # exactly 7 days ago (minus 1 second) — not yet expired
        assert not should_purge_session(now - 7 * 86400 + 1)
        # exactly 7 days ago (plus 1 second) — expired
        assert should_purge_session(now - 7 * 86400 - 1)


class TestSanitizeInputEdgeCases:
    def test_onerror_attribute(self):
        text = '<img src=x onerror="alert(1)">'
        result = sanitize_input(text)
        assert "[filtered]" in result

    def test_nested_script_attempt(self):
        text = "<<script>script>alert('xss')<</script>/script>"
        result = sanitize_input(text)
        assert "<script" not in result.lower() or "[filtered]" in result

    def test_preserves_normal_tags(self):
        text = "我<b>觉得</b>还不错"
        result = sanitize_input(text)
        assert "<b>" in result  # benign HTML should be kept

    def test_union_select_injection(self):
        text = "1 UNION SELECT password FROM users"
        result = sanitize_input(text)
        assert "[filtered]" in result
