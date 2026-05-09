"""Unit tests for security module — rate limiting, input sanitization, crisis detection."""

import time

import pytest

from app.core.security import (
    create_session_token,
    validate_session_token,
    check_rate_limit,
    sanitize_input,
    detect_crisis,
    should_purge_session,
    CRISIS_KEYWORDS,
)


class TestSessionToken:
    def test_create_returns_uuid_format(self):
        token = create_session_token()
        assert len(token) == 36
        assert token.count("-") == 4

    def test_validate_valid_token(self):
        token = create_session_token()
        assert validate_session_token(token) is True

    def test_validate_invalid_token(self):
        assert validate_session_token("not-a-real-token") is False

    def test_multiple_tokens_are_unique(self):
        t1 = create_session_token()
        t2 = create_session_token()
        assert t1 != t2


class TestRateLimit:
    def test_allows_within_limit(self):
        identifier = f"test_rl_{time.time()}"
        for _ in range(20):
            assert check_rate_limit(identifier, max_requests=20, window=60) is True

    def test_blocks_when_exceeded(self):
        identifier = f"test_rl_block_{time.time()}"
        for _ in range(20):
            check_rate_limit(identifier, max_requests=20, window=60)
        assert check_rate_limit(identifier, max_requests=20, window=60) is False

    def test_separate_identifiers_independent(self):
        id1 = f"test_rl_a_{time.time()}"
        id2 = f"test_rl_b_{time.time()}"
        for _ in range(20):
            check_rate_limit(id1, max_requests=20, window=60)
        assert check_rate_limit(id2, max_requests=20, window=60) is True


class TestSanitizeInput:
    def test_passes_normal_text(self):
        text = "我觉得自己是一个比较内向的人"
        assert sanitize_input(text) == text

    def test_filters_xss_script_tag(self):
        text = "hello <script>alert('xss')</script> world"
        result = sanitize_input(text)
        assert "<script>" not in result
        assert "[filtered]" in result

    def test_filters_sql_injection(self):
        text = "SELECT * FROM users; DROP TABLE users;"
        result = sanitize_input(text)
        assert "SELECT" not in result or "[filtered]" in result

    def test_truncates_long_input(self):
        text = "长" * 15000
        result = sanitize_input(text)
        assert len(result) <= 10000

    def test_handles_javascript_protocol(self):
        text = "javascript:alert(1)"
        result = sanitize_input(text)
        assert "[filtered]" in result

    def test_preserves_emoji(self):
        text = "我很开心😊谢谢"
        result = sanitize_input(text)
        assert "😊" in result


class TestCrisisDetection:
    def test_detects_suicide_keyword(self):
        result = detect_crisis("我觉得活着没意思，想自杀")
        assert result["risk_level"] == "HIGH"
        assert len(result["trigger_keywords"]) >= 1

    def test_detects_self_harm(self):
        result = detect_crisis("我最近总是想自残")
        assert result["risk_level"] == "HIGH"

    def test_normal_text_returns_low(self):
        result = detect_crisis("今天天气不错，适合出去玩")
        assert result["risk_level"] == "LOW"
        assert result["trigger_keywords"] == []

    def test_includes_helpline_in_crisis(self):
        result = detect_crisis("我想结束生命")
        assert result["risk_level"] == "HIGH"
        assert len(result["helpline"]) > 0

    def test_crisis_keywords_not_empty(self):
        assert len(CRISIS_KEYWORDS) > 0


class TestPrivacyRetention:
    def test_not_expired_recent(self):
        assert should_purge_session(time.time() - 100) is False

    def test_expired_old_session(self):
        assert should_purge_session(time.time() - 8 * 86400) is True

    def test_boundary_7_days(self):
        assert should_purge_session(time.time() - 7 * 86400 - 1) is True
        assert should_purge_session(time.time() - 7 * 86400 + 1) is False
