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

    def render_html(self, report: dict) -> str:
        """将报告渲染为独立 HTML 文件（内联 CSS）"""
        skeleton = report.get("personality_skeleton", {})
        cognitive = report.get("cognitive_map", {})
        linguistic = report.get("linguistic_sketch", {})
        sbti = report.get("sbti_label", {})
        therapist_note = report.get("therapist_note", "")
        mbti = skeleton.get("mbti_type", "UNKNOWN")
        dims = skeleton.get("dimension_scores", {})
        confs = skeleton.get("confidence", {})
        keywords = linguistic.get("top_keywords", [])
        label = PERSONALITY_LABELS.get(mbti, "")

        dim_bars = ""
        dim_names = {"E_I": ("外向 E", "内向 I"), "S_N": ("感觉 S", "直觉 N"), "T_F": ("思维 T", "情感 F"), "J_P": ("判断 J", "感知 P")}
        for key, (left, right) in dim_names.items():
            score = dims.get(key, 0)
            conf = confs.get(key, 0)
            pct = int((score + 1) / 2 * 100)
            bar_color = "#C48059" if pct >= 50 else "#888D66"
            dim_bars += f"""
            <div style="margin-bottom:16px">
              <div style="display:flex;justify-content:space-between;font-size:13px;color:#53573D;margin-bottom:4px">
                <span>{left}</span><span style="color:#A86542;font-size:12px">置信度 {conf:.0%}</span><span>{right}</span>
              </div>
              <div style="background:#EDEFE6;border-radius:8px;height:10px">
                <div style="background:{bar_color};width:{pct}%;height:100%;border-radius:8px"></div>
              </div>
            </div>"""

        kw_tags = "".join(f'<span style="display:inline-block;background:#F4D9CC;color:#6B3922;padding:3px 12px;border-radius:14px;margin:4px;font-size:13px">{kw}</span>' for kw in keywords[:15])

        # Build cognitive_map dim bars
        cog_data = cognitive or {}
        cog_bars = ""
        scenario_labels = {"work": "工作情境", "relationship": "情感情境", "crisis": "危机情境"}
        for key, label in scenario_labels.items():
            scenario = cog_data.get(key, {})
            cog_bars += f'<div style="margin-bottom:20px"><h3 style="font-size:14px;color:#6B704F;margin-bottom:10px">{label}</h3>'
            for dim_key, (left, right) in dim_names.items():
                score = scenario.get(dim_key, 0)
                pct = int((score + 1) / 2 * 100)
                bar_color = "#C48059" if pct >= 50 else "#888D66"
                cog_bars += f"""
                <div style="margin-bottom:10px">
                  <div style="display:flex;justify-content:space-between;font-size:12px;color:#53573D;margin-bottom:2px">
                    <span>{left}</span><span>{right}</span>
                  </div>
                  <div style="background:#EDEFE6;border-radius:8px;height:8px">
                    <div style="background:{bar_color};width:{pct}%;height:100%;border-radius:8px"></div>
                  </div>
                </div>"""
            cog_bars += "</div>"

        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>人格分析报告 — {mbti}</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box }}
  body {{ font-family:"PingFang SC","Microsoft YaHei","Noto Sans SC",sans-serif; background:#FFFDF7; color:#3C3F2D; line-height:1.7; max-width:720px; margin:0 auto; padding:40px 24px }}
  h1 {{ text-align:center; font-size:28px; color:#53573D; margin-bottom:8px }}
  .subtitle {{ text-align:center; color:#A86542; font-size:14px; margin-bottom:32px }}
  .card {{ background:#fff; border-radius:16px; padding:24px; margin-bottom:20px; box-shadow:0 2px 12px rgba(83,55,61,0.06) }}
  .card h2 {{ font-size:16px; color:#6B704F; margin-bottom:16px; border-left:3px solid #C48059; padding-left:10px }}
  .mbti-badge {{ text-align:center; font-size:48px; font-weight:700; color:#C48059; letter-spacing:4px; margin:16px 0 }}
  .mbti-label {{ text-align:center; color:#888D66; font-size:15px; margin-bottom:16px }}
  .note {{ background:#FAEEE8; border-radius:12px; padding:20px; font-size:14px; line-height:1.9; color:#6B3922 }}
  .footer {{ text-align:center; color:#A3A884; font-size:12px; margin-top:40px }}
  @media print {{ body {{ background:#fff }} .card {{ box-shadow:none; border:1px solid #DADDCC }} }}
</style></head>
<body>
  <h1>人格织梦者</h1>
  <div class="subtitle">Persona Weaver — AI 心理人格分析报告</div>

  <div class="card">
    <h2>MBTI 类型</h2>
    <div class="mbti-badge">{mbti}</div>
    <div class="mbti-label">{label}</div>
  </div>

  <div class="card">
    <h2>四维度得分</h2>
    {dim_bars}
  </div>

  <div class="card">
    <h2>关键词云</h2>
    <div style="text-align:center">{kw_tags if kw_tags else '<span style="color:#A3A884">数据不足</span>'}</div>
    <div style="display:flex;justify-content:center;gap:24px;margin-top:16px;font-size:13px;color:#6B704F">
      <span>抽象词占比 {linguistic.get("abstract_ratio", 0):.0%}</span>
      <span>具象词占比 {linguistic.get("concrete_ratio", 0):.0%}</span>
    </div>
  </div>

  <div class="card">
    <h2>认知场景</h2>
    <p style="font-size:13px;color:#888D66;margin-bottom:12px">以下为三个典型场景下的人格维度投射</p>
    {cog_bars}
  </div>

  <div class="card">
    <h2>社交与灵魂</h2>
    <p style="font-size:14px;color:#53573D;margin-bottom:8px">{sbti.get("social_survival_guide", "")}</p>
    <p style="font-size:14px;color:#C48059">{sbti.get("soul_match_index", "")}</p>
  </div>

  <div class="note">{therapist_note}</div>

  <div class="footer">由 人格织梦者 (Persona Weaver) 生成 · 仅供自我探索参考</div>
</body></html>"""
