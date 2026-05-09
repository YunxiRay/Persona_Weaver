import uuid

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    phase: Mapped[str] = mapped_column(
        Enum("RAPPORT", "EXPLORATION", "CONFRONTATION", "SYNTHESIS", "ENDED", name="phase_enum"),
        default="RAPPORT",
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        Enum("ACTIVE", "COMPLETED", "ABORTED", name="status_enum"),
        default="ACTIVE",
        nullable=False,
    )
    started_at: Mapped[str] = mapped_column(String, nullable=False, server_default="now()")
    ended_at: Mapped[str | None] = mapped_column(String, nullable=True)

    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session")
    dimension_snapshots = relationship("DimensionSnapshot", back_populates="session")
    report = relationship("Report", back_populates="session", uselist=False)
