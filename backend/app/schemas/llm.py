from pydantic import BaseModel, Field


class UpdatedDimension(BaseModel):
    E_I: float = Field(ge=-1.0, le=1.0)
    S_N: float = Field(ge=-1.0, le=1.0)
    T_F: float = Field(ge=-1.0, le=1.0)
    J_P: float = Field(ge=-1.0, le=1.0)


class UpdatedConfidence(BaseModel):
    E_I: float = Field(ge=0.0, le=1.0)
    S_N: float = Field(ge=0.0, le=1.0)
    T_F: float = Field(ge=0.0, le=1.0)
    J_P: float = Field(ge=0.0, le=1.0)


class SafetyFlags(BaseModel):
    risk_level: str = Field(default="LOW")  # LOW | MEDIUM | HIGH
    trigger_keywords: list[str] = Field(default_factory=list)


class InternalAnalysis(BaseModel):
    session_phase: str  # RAPPORT | EXPLORATION | CONFRONTATION | SYNTHESIS
    updated_dimensions: UpdatedDimension
    updated_confidence: UpdatedConfidence
    safety_flags: SafetyFlags = Field(default_factory=SafetyFlags)
    defense_flags: list[str] = Field(default_factory=list)  # avoidance, idealization, devaluation, splitting
    current_target: str = ""
    strategy: str = ""
    pattern_references: list[str] = Field(default_factory=list)  # RAG 检索匹配到的模式名称


class LLMStructuredOutput(BaseModel):
    """LLM 强制输出的结构化 JSON Schema"""
    doctor_reply: str
    is_final_report: bool = False
    internal_analysis: InternalAnalysis
    next_action_hint: str = ""  # EXPECT_LONG_INPUT | EXPECT_SHORT_INPUT | NORMAL


class DimensionScores(BaseModel):
    E_I: float
    S_N: float
    T_F: float
    J_P: float


class PersonalitySkeleton(BaseModel):
    mbti_type: str
    dimension_scores: DimensionScores
    confidence: UpdatedConfidence


class CognitiveMap(BaseModel):
    work: DimensionScores
    relationship: DimensionScores
    crisis: DimensionScores


class LinguisticSketch(BaseModel):
    style_label: str = ""
    top_keywords: list[str] = Field(default_factory=list)
    abstract_ratio: float = 0.0
    concrete_ratio: float = 0.0


class SBTILabel(BaseModel):
    social_survival_guide: str = ""
    soul_match_index: str = ""


class ReportSchema(BaseModel):
    """完整报告 JSON Schema"""
    personality_skeleton: PersonalitySkeleton
    cognitive_map: CognitiveMap
    linguistic_sketch: LinguisticSketch
    sbti_label: SBTILabel
    therapist_note: str = ""
