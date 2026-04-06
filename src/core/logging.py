import sys

from loguru import logger


def setup_logging():
    """Простое логирование только в терминал"""
    logger.remove()  # убираем дефолтный handler

    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True,
    )

    logger.info("Логирование настроено")
