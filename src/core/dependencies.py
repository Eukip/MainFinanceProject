"""FastAPI Dependencies + JWT авторизация"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.user_repository_port import UserRepository
from src.core.config import settings
from src.core.database import get_db
from src.domains.users.models import User
from src.domains.users.schemas import TokenPayload
from src.domains.users.service import UserService
from src.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository

# Простая Bearer-схема (одно поле для токена)
http_bearer = HTTPBearer()


# Dependency: возвращает готовый репозиторий
def get_user_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> UserRepository:
    """Инжектим конкретный Adapter через Port"""
    return SQLAlchemyUserRepository(db)


# Dependency: возвращает готовый сервис
def get_user_service(
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    """Инжектим сервис с правильным репозиторием"""
    return UserService(repository)


# Dependency: текущий авторизованный пользователь (JWT)
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> User:
    """Извлекает пользователя из Bearer-токена"""
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить учётные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        token_data = TokenPayload(**payload)
        if token_data.type != "access":
            raise credentials_exception
        email: str = token_data.sub
    except JWTError:
        raise credentials_exception from None

    user = await repository.get_by_email(email)
    if user is None:
        raise credentials_exception

    return user
