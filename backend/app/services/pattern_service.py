"""模式库服务 — PatternService (DB CRUD) + PatternRetriever (内存向量索引)"""

import uuid

import numpy as np
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.psychology_pattern import PsychologyPattern

logger = structlog.get_logger(__name__)


class PatternService:
    """心理学模式数据库 CRUD"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        name: str,
        category: str,
        description: str,
        pattern_text: str,
        dimension_labels: dict | None = None,
        mbti_tags: list | None = None,
        defense_tags: list | None = None,
        phase_tags: list | None = None,
        vector_data: list[float] | None = None,
        is_active: bool = True,
    ) -> PsychologyPattern:
        pattern = PsychologyPattern(
            name=name,
            category=category,
            description=description,
            pattern_text=pattern_text,
            dimension_labels=dimension_labels or {},
            mbti_tags=mbti_tags or [],
            defense_tags=defense_tags or [],
            phase_tags=phase_tags or [],
            vector_data=vector_data,
            is_active=is_active,
        )
        self.db.add(pattern)
        await self.db.commit()
        await self.db.refresh(pattern)
        return pattern

    async def bulk_create(self, patterns: list[dict]) -> list[PsychologyPattern]:
        results = []
        for p in patterns:
            result = await self.create(**p)
            results.append(result)
        return results

    async def list_active(self) -> list[PsychologyPattern]:
        result = await self.db.execute(
            select(PsychologyPattern).where(PsychologyPattern.is_active == True)
        )
        return list(result.scalars().all())

    async def get_by_id(self, pattern_id: uuid.UUID) -> PsychologyPattern | None:
        result = await self.db.execute(
            select(PsychologyPattern).where(PsychologyPattern.id == pattern_id)
        )
        return result.scalar_one_or_none()


class PatternRetriever:
    """内存向量索引 — 启动时加载全部活跃向量"""

    def __init__(self):
        self._vectors: np.ndarray | None = None  # [N, 1024]
        self._patterns: list[dict] = []
        self._id_to_idx: dict[str, int] = {}

    @property
    def is_ready(self) -> bool:
        return self._vectors is not None and len(self._vectors) > 0

    async def build_index(self, db: AsyncSession) -> None:
        """从数据库加载所有活跃模式向量到 numpy 数组"""
        svc = PatternService(db)
        patterns = await svc.list_active()

        valid = [p for p in patterns if p.vector_data and len(p.vector_data) == 1024]
        if not valid:
            logger.warning("retriever_no_valid_patterns")
            return

        vectors = np.array([p.vector_data for p in valid], dtype=np.float32)
        # L2 预归一化，确保 dot product = cosine similarity
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1.0, norms)
        self._vectors = vectors / norms

        self._patterns = [
            {
                "id": str(p.id),
                "name": p.name,
                "category": p.category,
                "description": p.description,
                "pattern_text": p.pattern_text,
                "dimension_labels": p.dimension_labels or {},
                "mbti_tags": p.mbti_tags or [],
                "defense_tags": p.defense_tags or [],
                "phase_tags": p.phase_tags or [],
            }
            for p in valid
        ]
        self._id_to_idx = {p["id"]: i for i, p in enumerate(self._patterns)}
        logger.info("retriever_index_built", count=len(self._patterns))

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5,
        phase: str | None = None,
        defense_flags: list[str] | None = None,
    ) -> list[dict]:
        """检索 Top-K 相似模式。query_vector 需已 L2 归一化。"""
        if not self.is_ready:
            return []

        # dot product = cosine similarity (vectors are L2-normalized)
        scores = self._vectors @ query_vector  # [N]

        # Tag boosting
        for i, pattern in enumerate(self._patterns):
            boost = 0.0
            if phase and phase in pattern["phase_tags"]:
                boost += 0.05
            if defense_flags:
                for flag in defense_flags:
                    if flag in pattern["defense_tags"]:
                        boost += 0.10
            scores[i] += boost

        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            if scores[idx] >= 0.3:  # 最低相似度阈值
                p = self._patterns[idx]
                results.append({
                    "pattern_id": p["id"],
                    "name": p["name"],
                    "category": p["category"],
                    "description": p["description"],
                    "score": float(scores[idx]),
                    "dimension_labels": p["dimension_labels"],
                    "mbti_tags": p["mbti_tags"],
                })
        return results


_retriever: PatternRetriever | None = None


def get_retriever() -> PatternRetriever:
    global _retriever
    if _retriever is None:
        _retriever = PatternRetriever()
    return _retriever
