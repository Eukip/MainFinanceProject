from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import UUIDBase


class User(UUIDBase):
    """Пользователь приложения"""

    __tablename__ = "users"

    # Основная связка: email + пароль
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Статусы
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Двухфакторная аутентификация
    is_two_factor_enabled: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Связи
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
        # lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<User(email={self.email})>"


class RefreshToken(UUIDBase):
    """Refresh Token для безопасной ротации и отзыва"""
    __tablename__ = "refresh_tokens"

    token: Mapped[str] = mapped_column(
            String(512),
            unique=True,
            index=True,
            nullable=False,
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    # Срок жизни
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    # Статус токена
    revoked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    # Для Token Rotation и Reuse Detection
    previous_token: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
    )
    # === Device / Session fingerprinting ===
    # Информация, которую мы можем показать пользователю
    device_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Пользовательское название устройства (например: 'MacBook Pro', 'Samsung S23')",
    )
    user_agent: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
        comment="User-Agent браузера/приложения",
    )
    # Чувствительные данные — храним в хэшированном виде
    ip_address: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        comment="Хэш IP-адреса (SHA-256 или Argon2)",
    )
    device_fingerprint: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        comment="Хэш отпечатка устройства (экран, ОС, браузер и т.д.)",
    )
    # Обратная связь
    user: Mapped["User"] = relationship(
        "User",
        back_populates="refresh_tokens",
    )

    def is_expired(self) -> bool:
        """Проверяет, истёк ли токен"""
        return datetime.now(timezone.utc) > self.expires_at

    def __repr__(self) -> str:
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, revoked={self.revoked})>"
