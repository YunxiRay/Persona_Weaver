import uuid

from sqlalchemy import Boolean, JSON, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PsychologyPattern(Base):
    __tablename__ = "psychology_patterns"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    pattern_text: Mapped[str] = mapped_column(Text, nullable=False)
    dimension_labels: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    mbti_tags: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    defense_tags: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    phase_tags: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    vector_data: Mapped[list[float] | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[str] = mapped_column(String, nullable=False, server_default="now()")
