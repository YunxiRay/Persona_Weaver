from pydantic import BaseModel, Field


class PatternSearchRequest(BaseModel):
    text: str
    top_k: int = Field(default=5, ge=1, le=10)
    phase: str | None = None
    defense_flags: list[str] = Field(default_factory=list)


class PatternReference(BaseModel):
    pattern_id: str
    name: str
    category: str
    description: str
    score: float


class PatternSearchResponse(BaseModel):
    patterns: list[PatternReference]
