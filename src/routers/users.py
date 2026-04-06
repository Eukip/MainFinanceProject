"""HTTP-роутеры для домена Users"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from src.core.dependencies import get_current_user, get_user_service
from src.domains.users.models import User
from src.domains.users.schemas import Token, UserCreate, UserLogin, UserRead
from src.domains.users.service import UserService

router = APIRouter(prefix="/users", tags=["auth"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    """Регистрация нового пользователя"""
    try:
        return await user_service.register(user_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post("/login", response_model=Token)
async def login_user(
    user_in: UserLogin,
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    """Логин пользователя"""
    try:
        return await user_service.authenticate(user_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


@router.get("/me", response_model=UserRead)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Получить данные текущего авторизованного пользователя"""
    return UserRead.model_validate(current_user)
