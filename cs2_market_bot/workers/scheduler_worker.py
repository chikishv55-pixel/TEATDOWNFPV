"""Воркер для запуска планировщика задач."""
import asyncio
import signal
from core.logging import logger
from core.database import init_db, close_db
from core.config import settings
from market.mock_provider import MockMarketProvider
from workers.scheduler import TaskScheduler


async def main():
    """Запуск воркера с планировщиком."""
    logger.info("Starting scheduler worker...")

    # Инициализация БД
    await init_db()
    logger.info("Database initialized")

    # Создание провайдера
    if settings.market_provider == "mock":
        provider = MockMarketProvider(fee_percent=settings.fee_percent)
    else:
        # Здесь будет создание реального провайдера
        provider = MockMarketProvider(fee_percent=settings.fee_percent)
        logger.warning(f"Provider '{settings.market_provider}' not implemented, using Mock")

    # Создание и запуск планировщика
    scheduler = TaskScheduler(provider)
    scheduler.start()

    # Обработка сигналов остановки
    loop = asyncio.get_event_loop()
    stop_event = asyncio.Event()

    def handle_signal():
        logger.info("Stop signal received")
        stop_event.set()

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, handle_signal)

    # Ожидание сигнала остановки
    await stop_event.wait()

    # Остановка планировщика
    scheduler.stop()
    await close_db()
    logger.info("Scheduler worker stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
