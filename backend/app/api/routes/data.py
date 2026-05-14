from fastapi import APIRouter

from app.core.persistence import clear_all_data

router = APIRouter(tags=["data"])


@router.delete("/data")
async def clear_data():
    """清除所有本地存储的历史记录、报告和配置"""
    cleared = clear_all_data()

    # 清空内存中的状态
    try:
        from app.api.routes.config import _config_store
        from app.engine.chat_pipeline import _sessions, _reports

        _config_store.clear()
        _sessions.clear()
        _reports.clear()
    except Exception:
        pass

    return {"status": "ok", "cleared": cleared}
