import random

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prompt import PromptTemplate


class PromptRegistry:
    """提示词模板注册表：从数据库加载版本化模板，支持按阶段和难度查询"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_for_phase(self, phase: str, difficulty: str = "standard") -> str | None:
        result = await self.db.execute(
            select(PromptTemplate)
            .where(
                PromptTemplate.phase == phase,
                PromptTemplate.difficulty == difficulty,
                PromptTemplate.is_active == True,
            )
            .order_by(PromptTemplate.version.desc())
            .limit(1)
        )
        tmpl = result.scalar_one_or_none()
        return tmpl.template_text if tmpl else None

    async def get_random_for_phase(self, phase: str) -> str | None:
        result = await self.db.execute(
            select(PromptTemplate).where(
                PromptTemplate.phase == phase,
                PromptTemplate.is_active == True,
            )
        )
        templates = list(result.scalars().all())
        if not templates:
            return None
        return random.choice(templates).template_text

    async def list_active(self) -> list[PromptTemplate]:
        result = await self.db.execute(
            select(PromptTemplate)
            .where(PromptTemplate.is_active == True)
            .order_by(PromptTemplate.phase, PromptTemplate.difficulty)
        )
        return list(result.scalars().all())
