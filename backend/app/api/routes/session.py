import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.engine.chat_pipeline import _reports
from app.services.session_service import SessionService

router = APIRouter(prefix="/session", tags=["session"])


@router.post("/{session_id}/complete")
async def complete_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """手动结束会话，触发报告生成"""
    try:
        sid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的 session_id")

    svc = SessionService(db)
    session = await svc.get_by_id(sid)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    session = await svc.complete(sid)

    report = _reports.get(session_id)
    return {
        "session_id": str(sid),
        "status": "completed",
        "report": report,
    }
