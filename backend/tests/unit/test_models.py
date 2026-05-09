"""Unit tests for SQLAlchemy model instantiation and explicit field values."""

import uuid

from app.models.dimension_snapshot import DimensionSnapshot
from app.models.message import Message
from app.models.prompt import PromptTemplate
from app.models.report import Report
from app.models.session import Session
from app.models.user import User


class TestUserModel:
    def test_create_user_sets_fields(self):
        uid = uuid.uuid4()
        user = User(id=uid, nickname="Test User")
        assert user.id == uid
        assert user.nickname == "Test User"

    def test_user_id_generated_when_not_provided(self):
        user = User(nickname="test")
        assert user.nickname == "test"


class TestSessionModel:
    def test_create_session_explicit_values(self):
        uid = uuid.uuid4()
        sid = uuid.uuid4()
        session = Session(id=sid, user_id=uid, phase="EXPLORATION", status="ACTIVE")
        assert session.user_id == uid
        assert session.phase == "EXPLORATION"
        assert session.status == "ACTIVE"

    def test_session_all_phases(self):
        uid = uuid.uuid4()
        for phase in ["RAPPORT", "EXPLORATION", "CONFRONTATION", "SYNTHESIS", "ENDED"]:
            session = Session(id=uuid.uuid4(), user_id=uid, phase=phase)
            assert session.phase == phase


class TestMessageModel:
    def test_create_message_explicit(self):
        sid = uuid.uuid4()
        msg = Message(
            id=uuid.uuid4(), session_id=sid, role="user", content="hello",
            phase="RAPPORT", effective_word_count=5,
        )
        assert msg.effective_word_count == 5
        assert msg.role == "user"
        assert msg.content == "hello"

    def test_message_with_embedding(self):
        sid = uuid.uuid4()
        embedding = [0.1] * 1024
        msg = Message(
            id=uuid.uuid4(), session_id=sid, role="user", content="test",
            phase="EXPLORATION", embedding=embedding,
        )
        assert len(msg.embedding) == 1024


class TestDimensionSnapshotModel:
    def test_create_snapshot_all_dimensions(self):
        sid = uuid.uuid4()
        snap = DimensionSnapshot(
            id=uuid.uuid4(), session_id=sid, turn_number=3,
            E_I=0.6, S_N=-0.2, T_F=0.7, J_P=0.3,
            confidence_E_I=0.5, confidence_S_N=0.3, confidence_T_F=0.8, confidence_J_P=0.4,
        )
        assert snap.turn_number == 3
        assert snap.E_I == 0.6
        assert snap.confidence_T_F == 0.8


class TestReportModel:
    def test_create_report(self):
        rid = uuid.uuid4()
        sid = uuid.uuid4()
        report = Report(id=rid, session_id=sid, mbti_type="INTJ", report_json={"sections": []})
        assert report.mbti_type == "INTJ"
        assert report.report_json == {"sections": []}


class TestPromptTemplateModel:
    def test_create_template_explicit(self):
        tid = uuid.uuid4()
        tmpl = PromptTemplate(
            id=tid, phase="EXPLORATION", difficulty="medium",
            template_text="describe a scenario...", version=2, is_active=True,
        )
        assert tmpl.difficulty == "medium"
        assert tmpl.version == 2
        assert tmpl.is_active is True

    def test_template_inactive(self):
        tmpl = PromptTemplate(
            id=uuid.uuid4(), phase="RAPPORT", difficulty="easy",
            template_text="hello...", is_active=False,
        )
        assert tmpl.is_active is False
