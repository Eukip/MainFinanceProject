"""Adapter — конкретная реализация UserRepository на SQLAlchemy"""
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.user_repository_port import UserRepository
from src.domains.users.models import User
from src.domains.users.schemas import UserCreate


class SQLAlchemyUserRepository(UserRepository):
    """Конкретный адаптер для SQLAlchemy"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user_in: UserCreate, hashed_password: str) -> User:
        user = User(
            email=user_in.email,
            hashed_password=hashed_password,
        )
        self.db.add(user)
        await self.db.flush()          # Получаем ID сразу
        return user

    async def update_last_login(self, user_id: UUID) -> None:
        user = await self.get_by_id(user_id)
        if user:
            user.last_login_at = func.now()
            await self.db.flush()
