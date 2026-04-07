"""Port (абстрактный интерфейс) для репозитория пользователей"""

from abc import abstractmethod
from datetime import datetime
from typing import Protocol
from uuid import UUID

from src.domains.users.models import RefreshToken, User
from src.domains.users.schemas import UserCreate


class UserRepository(Protocol):
    """Абстрактный порт — контракт, который обязаны выполнять все репозитории"""

    # === Основные операции с пользователем ===
    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Найти пользователя по email"""

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        """Найти пользователя по ID"""

    @abstractmethod
    async def create(self, user_in: UserCreate, hashed_password: str) -> User:
        """Создать нового пользователя"""

    @abstractmethod
    async def update_last_login(self, user_id: UUID) -> None:
        """Обновить время последнего входа"""

    @abstractmethod
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
        """Создание нового refresh-токена с информацией об устройстве"""

    @abstractmethod
    async def get_refresh_token(self, token: str) -> RefreshToken | None:
        """Найти refresh токен"""

    @abstractmethod
    async def revoke_refresh_token(self, token: str) -> bool:
        """Отозвать (инвалидировать) один refresh токен"""

    @abstractmethod
    async def revoke_all_user_refresh_tokens(self, user_id: UUID) -> None:
        """Отозвать все refresh-токены пользователя (Например, при выхода со всех устройств)"""
