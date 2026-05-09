"""Unit tests for input validation."""

import pytest
from app.core.security import validate_user_input


class TestValidateUserInput:
    def test_accepts_normal_chinese(self):
        assert validate_user_input("我觉得自己是一个比较内向的人") is None

    def test_accepts_normal_english(self):
        assert validate_user_input("I think I am a creative person who enjoys art") is None

    def test_rejects_too_short_single_char(self):
        err = validate_user_input("好")
        assert err is not None
        assert "多说一些" in err

    def test_rejects_empty_after_strip(self):
        err = validate_user_input("  ")
        assert err is not None

    def test_rejects_pure_punctuation(self):
        err = validate_user_input("... !!! ,,, ???")
        assert err is not None
        assert "文字" in err

    def test_rejects_repeated_single_char(self):
        err = validate_user_input("哈哈哈哈哈哈哈哈")
        assert err is not None
        assert "完整的句子" in err

    def test_rejects_too_long_input(self):
        err = validate_user_input("这是一个很长的测试句子" * 600)  # ~6000 chars > 5000
        assert err is not None
        assert "太长" in err

    def test_accepts_boundary_min_length(self):
        assert validate_user_input("你好") is None

    def test_accepts_emoji_with_text(self):
        assert validate_user_input("今天心情很好😊👍") is None

    def test_accepts_mixed_cn_en(self):
        assert validate_user_input("我觉得这个idea不错") is None
