# src/main.py
"""Точка входа приложения — FastAPI"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.core.database import close_db, init_db
from src.core.logging import setup_logging
from src.routers.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Запуск и остановка приложения"""
    setup_logging()
    print("🚀 Приложение запускается...")
    await init_db()  # инициализация БД (пока можно закомментировать)
    yield
    await close_db()  # корректное закрытие соединений
    print("🛑 Приложение остановлено.")


app = FastAPI(
    title="Finance App",
    version="0.1.0",
    description="Учёт финансов",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS (для будущего фронтенда, Telegram-бота, десктопа)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # в продакшене замени на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем все роутеры
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "message": "🚀 Finance App запущен!",
        "version": app.version,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Простая проверка работоспособности"""
    return {"status": "healthy"}
