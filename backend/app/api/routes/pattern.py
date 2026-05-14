"""模式检索 REST API"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.llm.embedder import get_embedder
from app.schemas.pattern import PatternSearchRequest, PatternSearchResponse, PatternReference
from app.services.pattern_service import PatternService, get_retriever

router = APIRouter(prefix="/patterns", tags=["patterns"])


@router.post("/search", response_model=PatternSearchResponse)
async def search_patterns(body: PatternSearchRequest):
    embedder = get_embedder()
    if not embedder.is_ready:
        raise HTTPException(status_code=503, detail="嵌入模型未就绪，请稍后再试")

    retriever = get_retriever()
    if not retriever.is_ready:
        raise HTTPException(status_code=503, detail="模式索引未构建，请稍后再试")

    query_vec = embedder.encode_single(body.text)
    if query_vec is None:
        raise HTTPException(status_code=500, detail="文本编码失败")

    results = retriever.search(
        query_vec,
        top_k=body.top_k,
        phase=body.phase,
        defense_flags=body.defense_flags,
    )

    patterns = [
        PatternReference(
            pattern_id=r["pattern_id"],
            name=r["name"],
            category=r["category"],
            description=r["description"],
            score=r["score"],
        )
        for r in results
    ]

    return PatternSearchResponse(patterns=patterns)


@router.get("")
async def list_patterns(db: AsyncSession = Depends(get_db)):
    svc = PatternService(db)
    patterns = await svc.list_active()
    return [
        {
            "id": str(p.id),
            "name": p.name,
            "category": p.category,
            "description": p.description,
            "mbti_tags": p.mbti_tags,
            "phase_tags": p.phase_tags,
        }
        for p in patterns
    ]
