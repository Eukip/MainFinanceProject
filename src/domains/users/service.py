from datetime import datetime, timedelta, timezone
from uuid import UUID

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import jwt

from src.application.ports.user_repository_port import UserRepository
from src.core.config import settings
from src.domains.users.schemas import (
    Token,
    TokenPayload,
    UserCreate,
    UserLogin,
    UserRead,
)

# Современный и безопасный хешер (argon2)
pwd_hasher = PasswordHasher()


class UserService:
    """Сервис пользователей — вся бизнес-логика"""

    def __init__(self, repository: UserRepository):
        self.repository = repository

    # ====================== ХЕШИРОВАНИЕ ПАРОЛЕЙ ======================
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        try:
            pwd_hasher.verify(hashed_password, plain_password)
            return True
        except VerifyMismatchError:
            return False

    def get_password_hash(self, password: str) -> str:
        """Хеширование пароля с помощью Argon2"""
        return pwd_hasher.hash(password)

    # ====================== JWT ======================
    def create_access_token(self, subject: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode = TokenPayload(
            sub=subject,
            exp=int(expire.timestamp()),
            type="access",
        ).model_dump()
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

    def create_refresh_token(self, subject: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )
        to_encode = TokenPayload(
            sub=subject,
            exp=int(expire.timestamp()),
            type="refresh",
        ).model_dump()
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

    # ====================== БИЗНЕС-ЛОГИКА ======================
    async def register(self, user_in: UserCreate) -> Token:
        """Регистрация нового пользователя"""
        # Проверяем, существует ли уже пользователь
        if await self.repository.get_by_email(user_in.email):
            raise ValueError("Пользователь с таким email уже существует")

        # Хешируем пароль
        hashed_password = self.get_password_hash(user_in.password)
        user = await self.repository.create(user_in, hashed_password)

        # Генерируем токены
        access_token = self.create_access_token(user.email)
        refresh_token = self.create_refresh_token(user.email)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    async def authenticate(self, user_in: UserLogin) -> Token:
        """Аутентификация (логин)"""
        user = await self.repository.get_by_email(user_in.email)
        if not user or not self.verify_password(user_in.password, user.hashed_password):
            raise ValueError("Неверный email или пароль")

        if not user.is_active:
            raise ValueError("Пользователь неактивен")

        # Обновляем время последнего входа
        await self.repository.update_last_login(user.id)

        access_token = self.create_access_token(user.email)
        refresh_token = self.create_refresh_token(user.email)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    async def get_user_by_id(self, user_id: UUID) -> UserRead:
        """Получить пользователя по ID (для текущего пользователя)"""
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise ValueError("Пользователь не найден")
        return UserRead.model_validate(user)
