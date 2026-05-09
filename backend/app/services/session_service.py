import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session


class SessionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: uuid.UUID) -> Session:
        session = Session(user_id=user_id)
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def get_by_id(self, session_id: uuid.UUID) -> Session | None:
        result = await self.db.execute(select(Session).where(Session.id == session_id))
        return result.scalar_one_or_none()

    async def update_phase(self, session_id: uuid.UUID, phase: str) -> Session | None:
        session = await self.get_by_id(session_id)
        if session:
            session.phase = phase
            await self.db.commit()
            await self.db.refresh(session)
        return session

    async def complete(self, session_id: uuid.UUID) -> Session | None:
        session = await self.get_by_id(session_id)
        if session:
            session.status = "COMPLETED"
            session.phase = "ENDED"
            await self.db.commit()
            await self.db.refresh(session)
        return session

    async def abort(self, session_id: uuid.UUID) -> Session | None:
        session = await self.get_by_id(session_id)
        if session:
            session.status = "ABORTED"
            await self.db.commit()
            await self.db.refresh(session)
        return session

    async def list_by_user(self, user_id: uuid.UUID, limit: int = 20) -> list[Session]:
        result = await self.db.execute(
            select(Session).where(Session.user_id == user_id).order_by(Session.started_at.desc()).limit(limit)
        )
        return list(result.scalars().all())
