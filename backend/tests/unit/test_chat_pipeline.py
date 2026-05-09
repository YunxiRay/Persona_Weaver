"""Unit tests for chat pipeline (without real LLM calls)."""

from unittest.mock import AsyncMock, patch

import pytest

from app.engine.chat_pipeline import (
    SessionState,
    _build_system_prompt,
    _detect_crisis_keywords,
    _get_fallback_reply,
    _get_or_create_session,
    run_pipeline,
)
from app.llm.provider import ProviderConfig


class TestSessionState:
    def test_new_session(self):
        state = SessionState("test-id")
        assert state.session_id == "test-id"
        assert state.conductor.current_phase == "RAPPORT"

    def test_to_dict(self):
        state = SessionState("test-id")
        d = state.to_dict()
        assert d["session_id"] == "test-id"
        assert "conductor" in d


class TestGetOrCreateSession:
    def test_creates_new(self):
        state = _get_or_create_session(None)
        assert state.session_id
        assert state.conductor.current_phase == "RAPPORT"

    def test_reuses_existing(self):
        state1 = _get_or_create_session("abc-123")
        state1.conductor.advance(100)
        state2 = _get_or_create_session("abc-123")
        assert state2.conductor.turn_count == 1


class TestCrisisDetection:
    def test_detects_crisis(self):
        assert _detect_crisis_keywords("我想自杀")

    def test_detects_self_harm(self):
        assert _detect_crisis_keywords("自残")

    def test_normal_text_is_ok(self):
        assert not _detect_crisis_keywords("今天天气不错")
        assert not _detect_crisis_keywords("我有点难过但还好")


class TestFallbackReply:
    def test_rapport_fallback(self):
        reply = _get_fallback_reply("RAPPORT")
        assert "慢慢聊" in reply

    def test_exploration_fallback(self):
        reply = _get_fallback_reply("EXPLORATION")
        assert "细节" in reply

    def test_unknown_phase_fallback(self):
        reply = _get_fallback_reply("UNKNOWN")
        assert reply


class TestBuildSystemPrompt:
    def test_prompt_contains_phase_and_dimensions(self):
        state = SessionState("test")
        prompt = _build_system_prompt(state, "NORMAL", None)
        assert "RAPPORT" in prompt
        assert "E_I" in prompt
        assert "Persona Weaver" in prompt

    def test_prompt_contains_tone_info(self):
        state = SessionState("test")
        prompt = _build_system_prompt(state, "SOOTHE", "用户感到无助")
        assert "用户感到无助" in prompt
        assert "SOOTHE" in prompt
