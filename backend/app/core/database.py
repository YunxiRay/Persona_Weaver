from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

_engine = None
_async_session_factory = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_async_engine(settings.DATABASE_URL, echo=settings.APP_DEBUG, pool_size=20, max_overflow=10)
    return _engine


def get_session_factory():
    global _async_session_factory
    if _async_session_factory is None:
        _async_session_factory = async_sessionmaker(get_engine(), class_=AsyncSession, expire_on_commit=False)
    return _async_session_factory


class Base(DeclarativeBase):
    pass
