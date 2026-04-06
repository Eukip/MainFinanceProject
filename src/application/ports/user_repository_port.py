"""Port (абстрактный интерфейс) для репозитория пользователей"""
from abc import abstractmethod
from typing import Protocol
from uuid import UUID

from src.domains.users.models import User
from src.domains.users.schemas import UserCreate


class UserRepository(Protocol):
    """Абстрактный порт — контракт, который обязаны выполнять все репозитории"""

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
