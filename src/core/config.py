from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",  # игнорируем лишние переменные
    )

    # === Основные настройки ===
    PROJECT_NAME: str = "Main Finance App"
    API_V1_STR: str = "/api/v1"

    # === База данных ===
    DATABASE_URL: str
    SQLALCHEMY_ECHO: bool = False

    # === Безопасность (понадобится для JWT) ===
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 дней
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30    # 30 дней

    # === AI (пока оставляем, позже используем) ===
    OPENAI_API_KEY: str | None = None


# Создаём единственный экземпляр настроек
settings = Settings()
