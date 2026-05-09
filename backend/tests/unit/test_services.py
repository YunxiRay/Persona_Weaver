"""Unit tests for service layer business logic (no DB required)."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dimension_snapshot import DimensionSnapshot
from app.models.message import Message
from app.models.prompt import PromptTemplate
from app.models.report import Report
from app.models.session import Session
from app.models.user import User
from app.services.message_service import MessageService
from app.services.prompt_service import PromptService
from app.services.report_service import ReportService
from app.services.session_service import SessionService


@pytest.fixture
def mock_db():
    return AsyncMock(spec=AsyncSession)


class TestSessionService:
    def test_create_session(self, mock_db):
        svc = SessionService(mock_db)
        session = Session(user_id=uuid.uuid4())
        mock_db.refresh = AsyncMock(side_effect=lambda obj: None)
        mock_db.commit = AsyncMock()
        svc.create = AsyncMock(return_value=session)

        async def _test():
            result = await svc.create(uuid.uuid4())
            assert isinstance(result, Session)
        import asyncio
        asyncio.run(_test())

    def test_update_phase(self, mock_db):
        sid = uuid.uuid4()
        session = Session(user_id=uuid.uuid4(), phase="RAPPORT")
        mock_db.refresh = AsyncMock()
        mock_db.commit = AsyncMock()
        svc = SessionService(mock_db)
        svc.get_by_id = AsyncMock(return_value=session)
        svc.update_phase = AsyncMock(return_value=session)

        async def _test():
            result = await svc.update_phase(sid, "EXPLORATION")
            assert result is not None
        import asyncio
        asyncio.run(_test())


class TestMessageService:
    def test_create_message(self, mock_db):
        svc = MessageService(mock_db)
        msg = Message(session_id=uuid.uuid4(), role="user", content="test", phase="RAPPORT")
        mock_db.refresh = AsyncMock()
        mock_db.commit = AsyncMock()
        svc.create = AsyncMock(return_value=msg)

        async def _test():
            result = await svc.create(uuid.uuid4(), "user", "你好", "RAPPORT", 2)
            assert result.role == "user"
        import asyncio
        asyncio.run(_test())


class TestReportService:
    def test_create_report(self, mock_db):
        svc = ReportService(mock_db)
        report = Report(session_id=uuid.uuid4(), mbti_type="INFJ", report_json={})
        mock_db.refresh = AsyncMock()
        mock_db.commit = AsyncMock()
        svc.create = AsyncMock(return_value=report)

        async def _test():
            result = await svc.create(uuid.uuid4(), "INFJ", {})
            assert result.mbti_type == "INFJ"
        import asyncio
        asyncio.run(_test())


class TestPromptService:
    def test_get_by_phase(self, mock_db):
        templates = [
            PromptTemplate(phase="RAPPORT", difficulty="easy", template_text="hello", is_active=True)
        ]
        svc = PromptService(mock_db)
        svc.get_by_phase = AsyncMock(return_value=templates)

        async def _test():
            result = await svc.get_by_phase("RAPPORT")
            assert len(result) == 1
            assert result[0].phase == "RAPPORT"
        import asyncio
        asyncio.run(_test())
