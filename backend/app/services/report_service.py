import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.report import Report


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, session_id: uuid.UUID, mbti_type: str, report_json: dict) -> Report:
        report = Report(session_id=session_id, mbti_type=mbti_type, report_json=report_json)
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def get_by_session(self, session_id: uuid.UUID) -> Report | None:
        result = await self.db.execute(select(Report).where(Report.session_id == session_id))
        return result.scalar_one_or_none()

    async def get_by_id(self, report_id: uuid.UUID) -> Report | None:
        result = await self.db.execute(select(Report).where(Report.id == report_id))
        return result.scalar_one_or_none()
