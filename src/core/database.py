"""Настройка базы данных (Postgres + SQLAlchemy 2.0 async)"""

from collections.abc import AsyncGenerator
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, func
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from .config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.SQLALCHEMY_ECHO,  # выводит SQL в консоль при True
    pool_pre_ping=True,  # проверяет соединение перед использованием
)


async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: async with get_db() as db"""
    async with async_session() as session:
        yield session
        await session.commit()


class Base(DeclarativeBase):
    """Единый базовый класс для всех моделей проекта"""

    __abstract__ = True


class UUIDBase(Base):
    """Базовый класс для сущностей с UUID primary key"""

    __abstract__ = True

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


async def init_db() -> None:
    """Здесь можно делать create_all или другие инициализации"""
    pass


async def close_db() -> None:
    """Корректное закрытие соединений"""
    await engine.dispose()
