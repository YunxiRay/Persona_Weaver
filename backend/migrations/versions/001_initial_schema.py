"""Initial schema — all 6 tables + pgvector extension

Revision ID: 001
Revises:
Create Date: 2026-05-09
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("nickname", sa.String(100), nullable=False),
        sa.Column("created_at", sa.String(), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("phase", sa.Enum("RAPPORT", "EXPLORATION", "CONFRONTATION", "SYNTHESIS", "ENDED", name="phase_enum"), nullable=False, server_default="RAPPORT"),
        sa.Column("status", sa.Enum("ACTIVE", "COMPLETED", "ABORTED", name="status_enum"), nullable=False, server_default="ACTIVE"),
        sa.Column("started_at", sa.String(), nullable=False, server_default=sa.text("now()")),
        sa.Column("ended_at", sa.String(), nullable=True),
    )

    op.create_table(
        "messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sessions.id"), nullable=False),
        sa.Column("role", sa.Enum("user", "assistant", "system", name="role_enum"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("phase", sa.Enum("RAPPORT", "EXPLORATION", "CONFRONTATION", "SYNTHESIS", "ENDED", name="message_phase_enum"), nullable=False),
        sa.Column("effective_word_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("embedding", pgvector.sqlalchemy.Vector(1024), nullable=True),
        sa.Column("created_at", sa.String(), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "dimension_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sessions.id"), nullable=False),
        sa.Column("turn_number", sa.Integer(), nullable=False),
        sa.Column("E_I", sa.Float(), nullable=False),
        sa.Column("S_N", sa.Float(), nullable=False),
        sa.Column("T_F", sa.Float(), nullable=False),
        sa.Column("J_P", sa.Float(), nullable=False),
        sa.Column("confidence_E_I", sa.Float(), nullable=False),
        sa.Column("confidence_S_N", sa.Float(), nullable=False),
        sa.Column("confidence_T_F", sa.Float(), nullable=False),
        sa.Column("confidence_J_P", sa.Float(), nullable=False),
    )

    op.create_table(
        "reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sessions.id"), unique=True, nullable=False),
        sa.Column("mbti_type", sa.String(4), nullable=False),
        sa.Column("report_json", postgresql.JSON(), nullable=False),
        sa.Column("created_at", sa.String(), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "prompt_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("phase", sa.String(20), nullable=False),
        sa.Column("difficulty", sa.String(20), nullable=False),
        sa.Column("template_text", sa.Text(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )


def downgrade() -> None:
    op.drop_table("prompt_templates")
    op.drop_table("reports")
    op.drop_table("dimension_snapshots")
    op.drop_table("messages")
    op.drop_table("sessions")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS message_phase_enum")
    op.execute("DROP TYPE IF EXISTS role_enum")
    op.execute("DROP TYPE IF EXISTS status_enum")
    op.execute("DROP TYPE IF EXISTS phase_enum")
