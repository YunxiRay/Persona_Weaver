import uuid

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class DimensionSnapshot(Base):
    __tablename__ = "dimension_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    turn_number: Mapped[int] = mapped_column(Integer, nullable=False)

    E_I: Mapped[float] = mapped_column(Float, nullable=False)
    S_N: Mapped[float] = mapped_column(Float, nullable=False)
    T_F: Mapped[float] = mapped_column(Float, nullable=False)
    J_P: Mapped[float] = mapped_column(Float, nullable=False)

    confidence_E_I: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_S_N: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_T_F: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_J_P: Mapped[float] = mapped_column(Float, nullable=False)

    session = relationship("Session", back_populates="dimension_snapshots")
