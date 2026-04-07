"""Adapter — конкретная реализация UserRepository на SQLAlchemy"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.user_repository_port import UserRepository
from src.domains.users.models import RefreshToken, User
from src.domains.users.schemas import UserCreate


class SQLAlchemyUserRepository(UserRepository):
    """Конкретный адаптер для SQLAlchemy"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create(self, user_in: UserCreate, hashed_password: str) -> User:
        user = User(
            email=user_in.email,
            hashed_password=hashed_password,
        )
        self.db.add(user)
        await self.db.flush()  # Получаем ID сразу
        return user

    async def update_last_login(self, user_id: UUID) -> None:
        user = await self.get_by_id(user_id)
        if user:
            user.last_login_at = func.now()
            await self.db.flush()

    async def create_refresh_token(
        self,
        user_id: UUID,
        token: str,
        expires_at: datetime,
        device_name: str | None = None,
        user_agent: str | None = None,
        ip_address: str | None = None,
        device_fingerprint: str | None = None,
    ) -> RefreshToken:
        """Создаёт новый refresh-токен с информацией об устройстве"""
        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            revoked=False,
            device_name=device_name,
            user_agent=user_agent,
            ip_address=ip_address,
            device_fingerprint=device_fingerprint,
        )
        self.db.add(refresh_token)
        await self.db.flush()
        return refresh_token

    async def get_refresh_token(self, token: str) -> RefreshToken | None:
        """Найти refresh-токен по его строковому значению"""
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token == token)
        )
        return result.scalar_one_or_none()

    async def revoke_refresh_token(self, token: str) -> bool:
        """Отозвать один refresh-токен"""
        refresh_token = await self.get_refresh_token(token)
        if refresh_token and not refresh_token.revoked:
            refresh_token.revoked = True
            await self.db.flush()
            return True
        return False

    async def revoke_all_user_refresh_tokens(self, user_id: UUID) -> None:
        """Отозвать все refresh-токены пользователя (например, при logout со всех устройств)"""
        await self.db.execute(
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked.is_(False)
            )
            .values(revoked=True)
        )
        await self.db.flush()
