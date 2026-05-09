import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Message


class MessageService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        session_id: uuid.UUID,
        role: str,
        content: str,
        phase: str,
        effective_word_count: int = 0,
        embedding: list[float] | None = None,
    ) -> Message:
        message = Message(
            session_id=session_id,
            role=role,
            content=content,
            phase=phase,
            effective_word_count=effective_word_count,
            embedding=embedding,
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def list_by_session(self, session_id: uuid.UUID, limit: int = 100) -> list[Message]:
        result = await self.db.execute(
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_total_effective_words(self, session_id: uuid.UUID) -> int:
        result = await self.db.execute(
            select(func.coalesce(func.sum(Message.effective_word_count), 0)).where(
                Message.session_id == session_id, Message.role == "user"
            )
        )
        return result.scalar() or 0

    async def get_message_count(self, session_id: uuid.UUID) -> int:
        result = await self.db.execute(
            select(func.count(Message.id)).where(
                Message.session_id == session_id, Message.role == "user"
            )
        )
        return result.scalar() or 0
