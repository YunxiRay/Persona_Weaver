import json
import re

import structlog

from app.schemas.llm import LLMStructuredOutput

logger = structlog.get_logger(__name__)


def parse_llm_output(raw_content: str) -> LLMStructuredOutput | None:
    """解析 LLM 返回的 JSON，尝试多种策略提取结构化输出"""
    strategies = [
        _extract_json_block,
        _extract_brace_json,
        _find_json_like,
    ]

    for strategy in strategies:
        try:
            parsed = strategy(raw_content)
            if parsed:
                return LLMStructuredOutput.model_validate(parsed)
        except Exception:
            continue

    return None


def _extract_json_block(content: str) -> dict | None:
    """提取 ```json ... ``` 代码块"""
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
    if match:
        return json.loads(match.group(1))
    return None


def _extract_brace_json(content: str) -> dict | None:
    """提取最外层 { ... } JSON"""
    match = re.search(r"\{[\s\S]*\}", content)
    if match:
        return json.loads(match.group(0))
    return None


def _find_json_like(content: str) -> dict | None:
    """尝试寻找包含 doctor_reply 的 JSON 结构"""
    match = re.search(r'"doctor_reply"\s*:\s*"((?:[^"\\]|\\.)*)"', content)
    if match:
        return {
            "doctor_reply": json.loads(f'"{match.group(1)}"'),
            "is_final_report": False,
            "internal_analysis": {},
            "next_action_hint": "",
        }
    return None


def build_fallback_output(raw_content: str) -> LLMStructuredOutput:
    """LLM 输出无法解析时的降级回应"""
    from app.schemas.llm import InternalAnalysis, SafetyFlags, UpdatedConfidence, UpdatedDimension

    return LLMStructuredOutput(
        doctor_reply=raw_content[:500] or "我理解你的意思，能再多说说吗？",
        is_final_report=False,
        internal_analysis=InternalAnalysis(
            session_phase="RAPPORT",
            updated_dimensions=UpdatedDimension(E_I=0.0, S_N=0.0, T_F=0.0, J_P=0.0),
            updated_confidence=UpdatedConfidence(E_I=0.5, S_N=0.5, T_F=0.5, J_P=0.5),
            safety_flags=SafetyFlags(),
            current_target="",
            strategy="FALLBACK",
        ),
        next_action_hint="",
    )
