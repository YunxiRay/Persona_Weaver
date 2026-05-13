"""调试接口：推理测试端点，跳过 WebSocket 直接批量注入消息测试管道"""

import time
import uuid as _uuid

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.engine.chat_pipeline import run_pipeline
from app.llm.provider import ProviderConfig

router = APIRouter(prefix="/debug", tags=["debug"])


class InferenceTestRequest(BaseModel):
    provider: str = "deepseek"
    api_key: str = ""
    model: str = "deepseek-v4-flash"
    base_url: str = "https://api.deepseek.com"
    messages: list[str] = Field(min_length=1, max_length=30)


class PerRoundInfo(BaseModel):
    turn: int
    user_input: str
    phase: str
    phase_label: str
    llm_raw_dimensions: dict[str, float]
    llm_raw_confidence: dict[str, float]
    bayesian_scores: dict[str, float]
    bayesian_std: dict[str, float]
    bayesian_confidence: dict[str, float]
    mbti: str
    is_converged: bool
    defense_flags: list[str]
    doctor_reply: str = ""


class InferenceTestResponse(BaseModel):
    session_id: str
    rounds: list[PerRoundInfo]
    final_mbti: str
    mbti_history: list[str]
    mbti_stable_rounds: int = 0
    converged_at_round: int | None = None
    cognitive_map: dict | None = None
    total_llm_calls: int = 0
    elapsed_seconds: float = 0.0


@router.post("/inference-test", response_model=InferenceTestResponse)
async def inference_test(req: InferenceTestRequest):
    """批量注入模拟消息，运行完整推理管道，返回每轮详细状态。

    可用于：
    - 验证贝叶斯推理是否正确更新
    - 检查维度分数是否随时间变化（而非锁死）
    - 验证认知地图数据完整性
    - 无需 WebSocket 交互即可快速回归测试
    """
    from app.engine.chat_pipeline import _sessions, _reports
    from app.services.report_generator import ReportGenerator

    session_id = str(_uuid.uuid4())
    provider_cfg = ProviderConfig(
        provider=req.provider,
        api_key=req.api_key,
        base_url=req.base_url or None,
        model=req.model or None,
    )

    rounds: list[PerRoundInfo] = []
    converged_at: int | None = None
    started_at = time.perf_counter()

    for i, msg in enumerate(req.messages):
        try:
            result = await run_pipeline(
                user_input=msg,
                session_id=session_id,
                provider_cfg=provider_cfg if i == 0 else None,
            )
        except Exception as e:
            # 某轮失败时记录错误并继续
            rounds.append(PerRoundInfo(
                turn=i + 1,
                user_input=msg,
                phase="ERROR",
                phase_label="",
                llm_raw_dimensions={},
                llm_raw_confidence={},
                bayesian_scores={},
                bayesian_std={},
                bayesian_confidence={},
                mbti="????",
                is_converged=False,
                defense_flags=[],
                doctor_reply=f"ERROR: {str(e)}",
            ))
            continue

        # 获取 session 状态
        state = _sessions.get(session_id)
        if not state:
            continue

        bayesian = state.bayesian
        tracker_std = {d: round(t.std, 4) for d, t in bayesian.trackers.items()}

        is_conv = result.get("is_final", False)
        if is_conv and converged_at is None:
            converged_at = state.conductor.turn_count

        rounds.append(PerRoundInfo(
            turn=state.conductor.turn_count,
            user_input=msg,
            phase=state.conductor.current_phase,
            phase_label=result.get("phase_label", ""),
            llm_raw_dimensions=state.dimensions,
            llm_raw_confidence=state.confidence,
            bayesian_scores=bayesian.dimension_scores(),
            bayesian_std=tracker_std,
            bayesian_confidence=bayesian.confidence_values(),
            mbti=bayesian.determine_mbti(),
            is_converged=is_conv,
            defense_flags=result.get("defense_flags", []),
            doctor_reply=result.get("content", "")[:200],
        ))

    elapsed = round(time.perf_counter() - started_at, 2)
    state = _sessions.get(session_id)

    # 获取最终状态
    final_mbti = "????"
    mbti_history: list[str] = []
    mbti_stable = 0
    cognitive_map = None

    if state:
        bayesian = state.bayesian
        final_mbti = bayesian.determine_mbti()
        mbti_history = bayesian.mbti_history

        # 计算当前 MBTI 已稳定多少轮
        if mbti_history:
            last = mbti_history[-1]
            stable_count = 0
            for m in reversed(mbti_history):
                if m == last:
                    stable_count += 1
                else:
                    break
            mbti_stable = stable_count

        # 如果有报告则获取认知地图
        report_data = _reports.get(session_id)
        if report_data:
            cognitive_map = report_data.get("cognitive_map")
        else:
            # 手动生成认知地图
            try:
                gen = ReportGenerator()
                cognitive_map = gen.build_cognitive_map(bayesian).model_dump()
            except Exception:
                pass

    # Cleanup
    _sessions.pop(session_id, None)
    _reports.pop(session_id, None)

    return InferenceTestResponse(
        session_id=session_id,
        rounds=rounds,
        final_mbti=final_mbti,
        mbti_history=mbti_history,
        mbti_stable_rounds=mbti_stable,
        converged_at_round=converged_at,
        cognitive_map=cognitive_map,
        total_llm_calls=len(req.messages),
        elapsed_seconds=elapsed,
    )
