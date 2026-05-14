import uuid

from sqlalchemy import Enum, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("sessions.id"), nullable=False)
    role: Mapped[str] = mapped_column(
        Enum("user", "assistant", "system", name="role_enum"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    phase: Mapped[str] = mapped_column(
        Enum("RAPPORT", "EXPLORATION", "CONFRONTATION", "SYNTHESIS", "ENDED", name="message_phase_enum"),
        nullable=False,
    )
    effective_word_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[str] = mapped_column(String, nullable=False, server_default="now()")

    session = relationship("Session", back_populates="messages")
