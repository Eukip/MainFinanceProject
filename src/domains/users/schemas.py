from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class UserBase(BaseModel):
    """Общие поля, которые используются в нескольких схемах"""

    email: EmailStr
    model_config = ConfigDict(
        from_attributes=True,  # Позволяет конвертировать SQLAlchemy-модель → Pydantic
        str_strip_whitespace=True,  # Убирает лишние пробелы
    )


class UserCreate(UserBase):
    """Схема для регистрации нового пользователя"""

    password: str = Field(..., min_length=8, max_length=72, description="Пароль пользователя")
    password_confirm: str = Field(
        ..., min_length=8, max_length=72, description="Подтверждение пароля"
    )

    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.password != self.password_confirm:
            raise ValueError("Пароли не совпадают")
        return self


class UserLogin(BaseModel):
    """Схема для логина"""

    email: EmailStr
    password: str


class UserRead(UserBase):
    """Схема для ответа клиенту (без пароля и hashed_password)"""

    id: UUID
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login_at: datetime | None = None


class Token(BaseModel):
    """Полный JWT-ответ (access + refresh)"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Payload внутри JWT"""

    sub: str  # email пользователя
    exp: int  # время истечения
    type: str = "access"  # "access" или "refresh"


class RefreshTokenRequest(BaseModel):
    """Запрос на обновление access-токена"""

    refresh_token: str
