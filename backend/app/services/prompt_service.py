from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prompt import PromptTemplate


class PromptService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_phase(self, phase: str, difficulty: str | None = None) -> list[PromptTemplate]:
        stmt = select(PromptTemplate).where(
            PromptTemplate.phase == phase, PromptTemplate.is_active == True
        )
        if difficulty:
            stmt = stmt.where(PromptTemplate.difficulty == difficulty)
        stmt = stmt.order_by(PromptTemplate.version.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_active_templates(self) -> list[PromptTemplate]:
        result = await self.db.execute(
            select(PromptTemplate).where(PromptTemplate.is_active == True).order_by(PromptTemplate.phase, PromptTemplate.difficulty)
        )
        return list(result.scalars().all())

    async def get_by_phase_and_difficulty(self, phase: str, difficulty: str) -> PromptTemplate | None:
        result = await self.db.execute(
            select(PromptTemplate)
            .where(PromptTemplate.phase == phase, PromptTemplate.difficulty == difficulty, PromptTemplate.is_active == True)
            .order_by(PromptTemplate.version.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
