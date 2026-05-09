"""报告生成器 — 从会话数据聚合完整人格报告"""

import structlog

from app.engine.inference.bayesian import BayesianEngine
from app.engine.inference.semantic import analyze_abstract_concrete_ratio, extract_keywords
from app.llm.provider import BaseLLMProvider
from app.schemas.llm import (
    CognitiveMap,
    DimensionScores,
    LinguisticSketch,
    PersonalitySkeleton,
    ReportSchema,
    SBTILabel,
    UpdatedConfidence,
)

logger = structlog.get_logger(__name__)

# SBTI 趣味标签库
SBTI_GUIDES: dict[str, dict[str, str]] = {
    "INTJ": {"social": "建筑师社交法则：少而精的深度关系，拒绝浅社交", "soul": "与 ENFP 灵魂合拍指数 92%"},
    "INTP": {"social": "逻辑学家生存指南：找到一个能跟上你思维跳跃的人", "soul": "与 ENTJ 灵魂合拍指数 88%"},
    "ENTJ": {"social": "指挥官社交手册：擅长安抚众人的同时坚定达成目标", "soul": "与 INTP 灵魂合拍指数 88%"},
    "ENTP": {"social": "辩论家社交指南：把每一次社交变成有趣的思维实验", "soul": "与 INFJ 灵魂合拍指数 90%"},
    "INFJ": {"social": "提倡者社交法则：深度共情但保持边界", "soul": "与 ENTP 灵魂合拍指数 90%"},
    "INFP": {"social": "调停者生存指南：用温柔改变世界，但先保护好自己", "soul": "与 ENFJ 灵魂合拍指数 94%"},
    "ENFJ": {"social": "主人公社交手册：你是他人的光，但也需要被照亮", "soul": "与 INFP 灵魂合拍指数 94%"},
    "ENFP": {"social": "竞选者社交指南：你的热情是礼物，学会聚焦它", "soul": "与 INTJ 灵魂合拍指数 92%"},
    "ISTJ": {"social": "物流师社交法则：可靠是最好的社交货币", "soul": "与 ESFP 灵魂合拍指数 85%"},
    "ISFJ": {"social": "守卫者生存指南：你的温柔是世界的底色", "soul": "与 ESTP 灵魂合拍指数 83%"},
    "ESTJ": {"social": "总经理社交手册：效率与秩序是团队的基石", "soul": "与 ISFP 灵魂合拍指数 80%"},
    "ESFJ": {"social": "执政官社交指南：照顾好每个人的同时别忘了自己", "soul": "与 ISTP 灵魂合拍指数 82%"},
    "ISTP": {"social": "鉴赏家生存法则：用行动说话，沉默是金", "soul": "与 ESFJ 灵魂合拍指数 82%"},
    "ISFP": {"social": "探险家社交指南：艺术家的灵魂不需要太多解释", "soul": "与 ESTJ 灵魂合拍指数 80%"},
    "ESTP": {"social": "企业家社交法则：生命是一场冒险，去享受", "soul": "与 ISFJ 灵魂合拍指数 83%"},
    "ESFP": {"social": "表演者生存指南：舞台是你的，但后台也很重要", "soul": "与 ISTJ 灵魂合拍指数 85%"},
}

PERSONALITY_LABELS: dict[str, str] = {
    "INTJ": "战略建筑师 — 独立、果断、远见卓识",
    "INTP": "逻辑学家 — 理性、好奇、思维深邃",
    "ENTJ": "指挥官 — 大胆、富有想象力、天生的领导者",
    "ENTP": "辩论家 — 机智、好奇、善于思辨",
    "INFJ": "提倡者 — 理想主义、富有同情心、安静而坚定",
    "INFP": "调停者 — 诗意、善良、利他主义",
    "ENFJ": "主人公 — 富有魅力、鼓舞人心、关怀他人",
    "ENFP": "竞选者 — 热情、创造力、自由精神",
    "ISTJ": "物流师 — 务实、可靠、注重事实",
    "ISFJ": "守卫者 — 专注、温暖、保护欲强",
    "ESTJ": "总经理 — 高效、有条理、出色的管理者",
    "ESFJ": "执政官 — 热心、社交、关怀备至",
    "ISTP": "鉴赏家 — 大胆、务实、善于解决问题",
    "ISFP": "探险家 — 灵活、有魅力、随时准备探索",
    "ESTP": "企业家 — 聪明、精力充沛、敏锐",
    "ESFP": "表演者 — 自发、活力四射、善于交际",
}


class ReportGenerator:
    """人格报告生成器"""

    def __init__(self, provider: BaseLLMProvider | None = None):
        self.provider = provider

    def build_skeleton(self, engine: BayesianEngine) -> PersonalitySkeleton:
        dims = engine.dimension_scores()
        confs = engine.confidence_values()
        return PersonalitySkeleton(
            mbti_type=engine.determine_mbti(),
            dimension_scores=DimensionScores(E_I=dims["E_I"], S_N=dims["S_N"], T_F=dims["T_F"], J_P=dims["J_P"]),
            confidence=UpdatedConfidence(E_I=confs["E_I"], S_N=confs["S_N"], T_F=confs["T_F"], J_P=confs["J_P"]),
        )

    def build_cognitive_map(self, engine: BayesianEngine) -> CognitiveMap:
        dims = engine.dimension_scores()
        return CognitiveMap(
            work=DimensionScores(
                E_I=dims["E_I"] * 1.1,
                S_N=dims["S_N"] * 1.0,
                T_F=dims["T_F"] * 1.2,
                J_P=dims["J_P"] * 1.1,
            ),
            relationship=DimensionScores(
                E_I=dims["E_I"] * 0.8,
                S_N=dims["S_N"] * 0.9,
                T_F=dims["T_F"] * 1.1,
                J_P=dims["J_P"] * 0.7,
            ),
            crisis=DimensionScores(
                E_I=-dims["E_I"] * 0.5,
                S_N=dims["S_N"] * 0.8,
                T_F=dims["T_F"] * 0.6,
                J_P=-dims["J_P"] * 0.4,
            ),
        )

    def build_linguistic_sketch(self, all_messages: list[str]) -> LinguisticSketch:
        text = " ".join(all_messages)
        keywords = extract_keywords(all_messages, top_n=20)
        ratio = analyze_abstract_concrete_ratio(text)

        if ratio["abstract_ratio"] > 0.6:
            style = "抽象思考者 — 偏好概念与意象的表达"
        elif ratio["concrete_ratio"] > 0.6:
            style = "具象叙事者 — 偏好具体事实与感官细节"
        else:
            style = "均衡表达者 — 抽象概念与具体细节灵活切换"

        return LinguisticSketch(
            style_label=style,
            top_keywords=[k[0] for k in keywords],
            abstract_ratio=ratio["abstract_ratio"],
            concrete_ratio=ratio["concrete_ratio"],
        )

    def build_sbti_label(self, mbti_type: str) -> SBTILabel:
        guide = SBTI_GUIDES.get(mbti_type, {"social": "独特的你，不需要被标签定义", "soul": "与另一个独特的灵魂自然会相遇"})
        return SBTILabel(
            social_survival_guide=guide.get("social", ""),
            soul_match_index=guide.get("soul", ""),
        )

    async def generate_therapist_note(
        self,
        skeleton: PersonalitySkeleton,
        linguistic: LinguisticSketch,
        history: list[dict[str, str]],
    ) -> str:
        if not self.provider:
            return self._default_therapist_note(skeleton.mbti_type)

        context = "\n".join([f"{m['role']}: {m['content'][:200]}" for m in history[-20:]])
        prompt = f"""[角色] Persona Weaver 资深心理分析师
[任务] 基于完整人格画像，生成一段温暖有深度的心理医生寄语
[MBTI 类型] {skeleton.mbti_type}
[维度分数] E_I={skeleton.dimension_scores.E_I:.2f}, S_N={skeleton.dimension_scores.S_N:.2f}, T_F={skeleton.dimension_scores.T_F:.2f}, J_P={skeleton.dimension_scores.J_P:.2f}
[语言风格] {linguistic.style_label}
[对话摘要] {context[:1500]}

请用温暖、真诚、非评判的语气，写一段 200-300 字的寄语。内容包括：
1. 对用户人格特质的深度共情
2. 一个温和的成长建议
3. 一句话的祝福
只返回寄语文本，不需要 JSON。"""

        try:
            resp = await self.provider.chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=600,
            )
            return resp.content.strip()
        except Exception as e:
            logger.error("therapist_note_generation_failed", error=str(e))
            return self._default_therapist_note(skeleton.mbti_type)

    async def generate(
        self,
        engine: BayesianEngine,
        all_messages: list[str],
        history: list[dict[str, str]],
    ) -> dict:
        skeleton = self.build_skeleton(engine)
        cognitive = self.build_cognitive_map(engine)
        linguistic = self.build_linguistic_sketch(all_messages)
        sbti = self.build_sbti_label(skeleton.mbti_type)
        therapist_note = await self.generate_therapist_note(skeleton, linguistic, history)

        report = ReportSchema(
            personality_skeleton=skeleton,
            cognitive_map=cognitive,
            linguistic_sketch=linguistic,
            sbti_label=sbti,
            therapist_note=therapist_note,
        )
        return report.model_dump()

    def _default_therapist_note(self, mbti_type: str) -> str:
        label = PERSONALITY_LABELS.get(mbti_type, "独一无二的个体")
        return (
            f"根据我们的对话，你的性格类型倾向为 {mbti_type}（{label}）。"
            f"你在对话中展现出了独特的思考方式和情感深度。"
            f"请记住，MBTI 只是理解自己的一个视角，每一个类型都有其独特的美与力量。"
            f"成长的关键不是成为别人，而是在了解自己的基础上，成为更好的自己。"
            f"愿你在自我探索的旅程中，不断发现新的惊喜。"
        )
