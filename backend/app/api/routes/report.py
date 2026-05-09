import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.engine.chat_pipeline import _reports
from app.services.report_service import ReportService

router = APIRouter(prefix="/report", tags=["report"])


@router.get("/session/{session_id}")
async def get_report_by_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """获取指定会话的人格分析报告"""
    try:
        sid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的 session_id")

    # Try in-memory first
    mem = _reports.get(session_id)
    if mem:
        mbti = mem.get("personality_skeleton", {}).get("mbti_type", "")
        return {"session_id": session_id, "mbti_type": mbti, "report": mem}

    # Try DB
    svc = ReportService(db)
    report = await svc.get_by_session(sid)
    if report:
        return {"report_id": str(report.id), "session_id": str(report.session_id), "mbti_type": report.mbti_type, "report": report.report_json, "created_at": report.created_at}

    raise HTTPException(status_code=404, detail="未找到该会话的报告")


@router.get("/{report_id}")
async def get_report_by_id(report_id: str, db: AsyncSession = Depends(get_db)):
    """通过报告 ID 获取报告"""
    try:
        rid = uuid.UUID(report_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的 report_id")

    svc = ReportService(db)
    report = await svc.get_by_id(rid)
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    return {"report_id": str(report.id), "session_id": str(report.session_id), "mbti_type": report.mbti_type, "report": report.report_json, "created_at": report.created_at}
