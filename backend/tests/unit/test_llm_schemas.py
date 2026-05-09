"""Unit tests for LLM output schemas and parser."""

import json

import pytest

from app.llm.output_parser import build_fallback_output, parse_llm_output
from app.schemas.llm import (
    InternalAnalysis,
    LLMStructuredOutput,
    SafetyFlags,
    UpdatedConfidence,
    UpdatedDimension,
)


class TestLLMStructuredOutput:
    def test_valid_output(self):
        data = {
            "doctor_reply": "我理解你的感受...",
            "is_final_report": False,
            "internal_analysis": {
                "session_phase": "EXPLORATION",
                "updated_dimensions": {"E_I": 0.5, "S_N": 0.2, "T_F": 0.7, "J_P": 0.3},
                "updated_confidence": {"E_I": 0.6, "S_N": 0.4, "T_F": 0.8, "J_P": 0.5},
                "safety_flags": {"risk_level": "LOW", "trigger_keywords": []},
                "current_target": "S_N",
                "strategy": "GENTLE_PROBE",
            },
            "next_action_hint": "EXPECT_LONG_INPUT",
        }
        output = LLMStructuredOutput.model_validate(data)
        assert output.doctor_reply == "我理解你的感受..."
        assert output.internal_analysis.session_phase == "EXPLORATION"
        assert output.internal_analysis.updated_dimensions.E_I == 0.5

    def test_invalid_dimension_range(self):
        data = {
            "doctor_reply": "test",
            "internal_analysis": {
                "session_phase": "RAPPORT",
                "updated_dimensions": {"E_I": 2.0, "S_N": 0.0, "T_F": 0.0, "J_P": 0.0},
                "updated_confidence": {"E_I": 0.5, "S_N": 0.5, "T_F": 0.5, "J_P": 0.5},
            },
        }
        with pytest.raises(Exception):
            LLMStructuredOutput.model_validate(data)


class TestParseLLMOutput:
    def test_parse_json_block(self):
        raw = '```json\n{"doctor_reply": "test", "internal_analysis": {"session_phase": "RAPPORT", "updated_dimensions": {"E_I": 0.1, "S_N": 0.2, "T_F": 0.3, "J_P": 0.4}, "updated_confidence": {"E_I": 0.5, "S_N": 0.5, "T_F": 0.5, "J_P": 0.5}}}\n```'
        result = parse_llm_output(raw)
        assert result is not None
        assert result.doctor_reply == "test"

    def test_parse_brace_json(self):
        raw = 'some text {"doctor_reply": "hello", "internal_analysis": {"session_phase": "RAPPORT", "updated_dimensions": {"E_I": 0.1, "S_N": 0.2, "T_F": 0.3, "J_P": 0.4}, "updated_confidence": {"E_I": 0.5, "S_N": 0.5, "T_F": 0.5, "J_P": 0.5}}} more text'
        result = parse_llm_output(raw)
        assert result is not None
        assert result.doctor_reply == "hello"

    def test_parse_garbage_returns_none(self):
        result = parse_llm_output("asdfghjkl not json here")
        assert result is None

    def test_fallback_output(self):
        fallback = build_fallback_output("some raw text")
        assert fallback.doctor_reply == "some raw text"
        assert fallback.internal_analysis.strategy == "FALLBACK"


class TestUpdatedDimension:
    def test_valid_range(self):
        dim = UpdatedDimension(E_I=0.5, S_N=-0.3, T_F=1.0, J_P=-1.0)
        assert dim.E_I == 0.5

    def test_out_of_range(self):
        with pytest.raises(Exception):
            UpdatedDimension(E_I=1.5, S_N=0.0, T_F=0.0, J_P=0.0)


class TestSafetyFlags:
    def test_default(self):
        flags = SafetyFlags()
        assert flags.risk_level == "LOW"
        assert flags.trigger_keywords == []
