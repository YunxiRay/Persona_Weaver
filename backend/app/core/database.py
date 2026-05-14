import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

_engine = None
_async_session_factory = None


def _resolve_database_url() -> str:
    url = settings.DATABASE_URL
    data_dir = os.environ.get("PW_DATA_DIR")
    if data_dir and url.startswith("sqlite+aiosqlite:///./"):
        db_name = url.rsplit("/", 1)[-1]
        url = f"sqlite+aiosqlite:///{data_dir}/{db_name}"
    return url


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            _resolve_database_url(),
            echo=settings.APP_DEBUG,
            connect_args={"check_same_thread": False},
        )
    return _engine


def get_session_factory():
    global _async_session_factory
    if _async_session_factory is None:
        _async_session_factory = async_sessionmaker(get_engine(), class_=AsyncSession, expire_on_commit=False)
    return _async_session_factory


class Base(DeclarativeBase):
    pass
