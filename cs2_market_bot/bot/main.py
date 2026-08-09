import asyncio
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from core.config import settings
from core.database import init_db, close_db
from core.logging import logger

# Импорты роутеров
from bot.handlers import start_router, help_router, signals_router, premium_router


def create_dispatcher() -> Dispatcher:
    """Создание и настройка диспетчера."""
    dp = Dispatcher()

    # Регистрируем роутеры
    dp.include_router(start_router)
    dp.include_router(help_router)
    dp.include_router(signals_router)
    dp.include_router(premium_router)

    return dp


async def main():
    """Основная функция запуска бота."""
    logger.info("Starting CS2 Market Bot...")

    # Инициализация БД
    await init_db()
    logger.info("Database initialized")

    # Создание бота
    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )

    # Создание диспетчера
    dp = create_dispatcher()

    try:
        # Запуск polling
        logger.info("Bot started successfully!")
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    finally:
        # Закрытие соединений
        await bot.session.close()
        await close_db()
        logger.info("Bot shutdown complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
