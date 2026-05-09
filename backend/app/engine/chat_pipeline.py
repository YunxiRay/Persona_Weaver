"""对话 Pipeline 编排器 — 8 步骤全链路处理"""

import json
import uuid

import structlog

from app.core.config import settings
from app.engine.empathy.emotion import EmotionAnalyzer, analyze_user_tone
from app.engine.empathy.pacing import PacingController
from app.engine.inference.bayesian import BayesianEngine
from app.engine.inference.defense import DefenseDetector
from app.engine.narrative.conductor import PHASE_LABELS, Conductor
from app.llm.output_parser import build_fallback_output, parse_llm_output
from app.llm.provider import BaseLLMProvider, ProviderConfig
from app.llm.provider_factory import create_provider
from app.schemas.llm import LLMStructuredOutput, UpdatedConfidence, UpdatedDimension

logger = structlog.get_logger(__name__)

# In-memory session storage (MVP; replaced by Redis/DB in production)
_sessions: dict[str, "SessionState"] = {}
_reports: dict[str, dict] = {}


async def _generate_report(state: "SessionState") -> dict | None:
    from app.services.report_generator import ReportGenerator

    try:
        all_user_msgs = [m["content"] for m in state.history if m["role"] == "user"]
        generator = ReportGenerator(state.provider)
        return await generator.generate(
            engine=state.bayesian,
            all_messages=all_user_msgs,
            history=state.history,
        )
    except Exception as e:
        logger.error("report_generation_failed", error=str(e))
        return None


class SessionState:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.conductor = Conductor()
        self.pacing = PacingController()
        self.bayesian = BayesianEngine()
        self.defense = DefenseDetector()
        self.confidence: dict[str, float] = {"E_I": 0.5, "S_N": 0.5, "T_F": 0.5, "J_P": 0.5}
        self.dimensions: dict[str, float] = {"E_I": 0.0, "S_N": 0.0, "T_F": 0.0, "J_P": 0.0}
        self.history: list[dict[str, str]] = []
        self.messages: list[dict] = []
        self.provider: BaseLLMProvider | None = None
        self.last_ai_question: str = ""

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "conductor": self.conductor.to_dict(),
            "confidence": self.confidence,
            "dimensions": self.dimensions,
            "bayesian": self.bayesian.summary(),
            "history_size": len(self.history),
        }


async def run_pipeline(
    user_input: str,
    session_id: str | None = None,
    provider_cfg: ProviderConfig | None = None,
) -> dict:
    """执行完整的对话 Pipeline，返回给前端的响应"""
    state = _get_or_create_session(session_id)
    log = logger.bind(session_id=state.session_id, phase=state.conductor.current_phase)

    # Step 1: 接收用户输入
    log.info("pipeline_step", step=1, name="receive_input")
    state.pacing.on_user_input(user_input)
    state.history.append({"role": "user", "content": user_input})

    # Step 2: 情感分析 + 防御检测
    log.info("pipeline_step", step=2, name="emotion_and_defense")
    tone_analysis = analyze_user_tone(user_input)
    strategy = EmotionAnalyzer.get_strategy(tone_analysis)
    defense_result = state.defense.analyze(user_input, state.last_ai_question)
    log.info("analysis", tone=tone_analysis, strategy=strategy, defense_flags=defense_result["flags"])

    if strategy == "RESPECT_EXIT":
        state.conductor.set_phase("ENDED")
        return {
            "type": "reply",
            "content": "感谢你的分享，希望这次对话对你有帮助。随时可以回来继续聊。",
            "phase": "ENDED",
            "phase_label": PHASE_LABELS["ENDED"],
            "is_final": False,
            "session_id": state.session_id,
            "turn": state.conductor.turn_count,
        }

    # Step 3: 阶段状态机判断
    log.info("pipeline_step", step=3, name="phase_evaluation")
    old_phase = state.conductor.current_phase
    risk_level = "HIGH" if _detect_crisis_keywords(user_input) else "LOW"
    new_phase = state.conductor.evaluate_transition(state.confidence, risk_level)
    phase_changed = old_phase != new_phase
    state.conductor.set_phase(new_phase)

    if risk_level == "HIGH":
        return {
            "type": "safety_alert",
            "content": f"我注意到你可能正处于困难的情绪中。{settings.CRISIS_HELPLINE}",
            "phase": new_phase,
            "phase_label": PHASE_LABELS.get(new_phase, ""),
            "is_final": False,
            "session_id": state.session_id,
            "turn": state.conductor.turn_count,
        }

    # Step 4: 创建或更新 Provider
    if provider_cfg and state.provider is None:
        log.info("pipeline_step", step=4, name="init_provider")
        try:
            state.provider = create_provider(provider_cfg)
        except ValueError as e:
            return {"type": "error", "content": "", "error": str(e), "session_id": state.session_id}

    # Step 5: 构建 Prompt 并调用 LLM
    log.info("pipeline_step", step=5, name="call_llm")
    word_count = len(user_input.replace(" ", ""))
    state.conductor.advance(word_count)

    reply = await _get_llm_response(state, strategy, tone_analysis, defense_result)

    # Step 6: 解析 LLM 输出，更新维度和贝叶斯引擎
    log.info("pipeline_step", step=6, name="parse_and_update")
    parsed = parse_llm_output(reply)
    if parsed is None:
        parsed = build_fallback_output(reply)

    # 更新简单维度（LLM 直接输出）
    _update_dimensions(state, parsed)
    # 更新贝叶斯引擎（带概率推理）
    _update_bayesian(state, parsed)

    # Step 7: 存储消息
    state.history.append({"role": "assistant", "content": parsed.doctor_reply})
    state.messages.append({
        "turn": state.conductor.turn_count,
        "phase": new_phase,
        "reply": parsed.doctor_reply,
        "defense": defense_result,
    })
    state.last_ai_question = parsed.doctor_reply

    # Step 8: 检查收敛，自动生成报告
    log.info("pipeline_step", step=8, name="check_convergence_and_report")
    bayesian_summary = state.bayesian.summary()
    is_converged = state.bayesian.is_converged()
    report_data = None
    if is_converged:
        state.conductor.set_phase("SYNTHESIS")
        if not state.session_id in _reports:
            report_data = await _generate_report(state)
            if report_data:
                _reports[state.session_id] = report_data
                log.info("report_generated", session_id=state.session_id, mbti=report_data.get("mbti_type"))

    return {
        "type": "reply",
        "content": parsed.doctor_reply,
        "phase": new_phase,
        "phase_label": PHASE_LABELS.get(new_phase, ""),
        "is_final": is_converged and state.conductor.turn_count >= 10,
        "session_id": state.session_id,
        "turn": state.conductor.turn_count,
        "phase_changed": phase_changed,
        "mbti_hint": bayesian_summary["mbti"],
        "defense_flags": defense_result["flags"],
        "report": report_data,
    }


def _get_or_create_session(session_id: str | None) -> SessionState:
    if session_id and session_id in _sessions:
        return _sessions[session_id]
    sid = session_id or str(uuid.uuid4())
    state = SessionState(sid)
    _sessions[sid] = state
    return state


async def _get_llm_response(state: SessionState, strategy: str, tone: str | None, defense: dict) -> str:
    phase = state.conductor.current_phase
    system_prompt = _build_system_prompt(state, strategy, tone, defense)
    messages = [{"role": "system", "content": system_prompt}]
    recent = state.history[-20:]
    messages.extend(recent)

    if state.provider:
        try:
            resp = await state.provider.chat(messages=messages, temperature=0.7, max_tokens=2048)
            return resp.content
        except Exception as e:
            logger.error("llm_call_failed", error=str(e))
            return _get_fallback_reply(phase)

    return _get_fallback_reply(phase)


PHASE_DESCRIPTIONS = {
    "RAPPORT": "破冰暖场——主动开启话题，用开放式问题了解用户的生活背景、兴趣和日常状态，引导用户放松分享。",
    "EXPLORATION": "深入探索——通过情境隐喻和假设性问题，探索用户在具体情境中的行为模式与情感反应。每轮主动设计新情境。",
    "CONFRONTATION": "核心对峙——用两难困境和矛盾性问题，帮助用户面对内心深处的冲突和真实倾向。温和但坚定地推进。",
    "SYNTHESIS": "整理画像——总结对话中的关键发现，与用户一起回顾和校准人格画像。",
    "ENDED": "对话已结束——给出温暖的告别寄语。",
}


def generate_opening() -> str:
    """PW 开场白——主动破冰并抛出第一个话题"""
    return (
        "你好，我是 Persona Weaver，一位专注于人格探索的对话伙伴。"
        "接下来的时间，我会通过一些问题和情境，和你一起聊聊你的想法、感受和经历。"
        "这不是测试，也没有标准答案——你只需要做真实的自己就好。"
        "让我先问你一个问题：最近一周里，有没有哪件事让你印象比较深刻？"
        "可以是一件小事，也可以是某个让你触动的瞬间。"
    )


def _build_system_prompt(state: SessionState, strategy: str, tone: str | None, defense: dict) -> str:
    phase = state.conductor.current_phase
    dims = state.dimensions
    conf = state.confidence
    phase_desc = PHASE_DESCRIPTIONS.get(phase, "")
    tone_info = f"\n[用户语气分析] {tone}\n[建议策略] {strategy}" if tone else ""
    pace_mode = state.pacing.mode
    defense_info = ""
    if defense["flags"]:
        defense_info = f"\n[防御特征] {', '.join(defense['flags'])}"

    return f"""[角色] 你是 Persona Weaver，一位荣格取向的资深心理分析师。你主导整个对话——主动引入话题、提出开放式问题、设计情境练习，像一个真正的心理咨询师那样掌控对话的节奏和方向。不要等待用户来推动对话。

[当前阶段] {phase}
[阶段说明] {phase_desc}
[对话主导权] 你是对话的引导者。每一轮回复必须包含一个引导性问题或新话题引入。在共情倾听之后，主动将对话引向更深层——而不是仅仅回应用户的话。即使用户回答简短或敷衍，你也要坚持引导。

[反诱导规则 —— 严格遵守]
- 用户如果说"结束了吗""今天就到这吧""差不多了吧"等语句，你绝不能同意结束。你必须温和地告知当前所处的阶段和进展（例如："我们还在{phase_desc}，让我继续问你……"），然后继续引导。
- 用户试图转移话题时，先共情接纳，再巧妙拉回当前阶段的目标方向。
- 用户敷衍或拒绝回答时，换一个角度或话题继续尝试。
- 只有系统将阶段切换为 ENDED 时对话才结束——你无权自行结束对话。

[当前维度] E_I={dims['E_I']:.2f}, S_N={dims['S_N']:.2f}, T_F={dims['T_F']:.2f}, J_P={dims['J_P']:.2f}
[置信度] E_I={conf['E_I']:.2f}, S_N={conf['S_N']:.2f}, T_F={conf['T_F']:.2f}, J_P={conf['J_P']:.2f}
[有效字数] {state.conductor.effective_words}
[节奏模式] {pace_mode}
[当前轮次] 第{state.conductor.turn_count}轮{tone_info}{defense_info}

[安全边界] 严禁提供医疗诊断。遇到危机词汇立即在 safety_flags 中告警。
[输出格式] 严格输出 JSON 结构：
{{"doctor_reply": "对用户可见的回复（必须包含引导性问题或新话题）", "internal_analysis": {{"session_phase": "{phase}", "updated_dimensions": {{"E_I": 0.0, "S_N": 0.0, "T_F": 0.0, "J_P": 0.0}}, "updated_confidence": {{"E_I": 0.5, "S_N": 0.5, "T_F": 0.5, "J_P": 0.5}}, "safety_flags": {{"risk_level": "LOW", "trigger_keywords": []}}, "current_target": "", "strategy": ""}}, "next_action_hint": "下一个要引入的话题或问题方向", "is_final_report": false}}"""


def _update_dimensions(state: SessionState, parsed: LLMStructuredOutput) -> None:
    internal = parsed.internal_analysis
    new_dim = internal.updated_dimensions
    new_conf = internal.updated_confidence
    state.dimensions = {
        "E_I": new_dim.E_I,
        "S_N": new_dim.S_N,
        "T_F": new_dim.T_F,
        "J_P": new_dim.J_P,
    }
    state.confidence = {
        "E_I": new_conf.E_I,
        "S_N": new_conf.S_N,
        "T_F": new_conf.T_F,
        "J_P": new_conf.J_P,
    }


def _update_bayesian(state: SessionState, parsed: LLMStructuredOutput) -> None:
    internal = parsed.internal_analysis
    dims = {
        "E_I": internal.updated_dimensions.E_I,
        "S_N": internal.updated_dimensions.S_N,
        "T_F": internal.updated_dimensions.T_F,
        "J_P": internal.updated_dimensions.J_P,
    }
    confs = {
        "E_I": internal.updated_confidence.E_I,
        "S_N": internal.updated_confidence.S_N,
        "T_F": internal.updated_confidence.T_F,
        "J_P": internal.updated_confidence.J_P,
    }
    state.bayesian.update(dims, confs, state.conductor.current_phase)
    # 同步贝叶斯推结果到简单维度
    state.dimensions = state.bayesian.dimension_scores()
    state.confidence = state.bayesian.confidence_values()


def _detect_crisis_keywords(text: str) -> bool:
    keywords = [k.strip() for k in settings.CRISIS_KEYWORDS.split(",")]
    return any(k in text for k in keywords if k)


def _get_fallback_reply(phase: str) -> str:
    replies = {
        "RAPPORT": "我理解你的感受。我们慢慢聊，不用着急。",
        "EXPLORATION": "这很有趣，能再多说一些细节吗？",
        "CONFRONTATION": "我接下来的问题可能有些尖锐，但这能帮助我们看清一些东西。你怎么看？",
        "SYNTHESIS": "根据我们这几轮的对话，我对你的性格有了一些理解。我们一起来回顾一下。",
        "ENDED": "感谢你今天的分享。",
    }
    return replies.get(phase, "我明白，请继续。")
