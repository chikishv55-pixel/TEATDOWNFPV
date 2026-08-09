from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import Optional

from core.logging import logger
from core.database import async_session_maker
from core.models import User, Subscription
from sqlalchemy import select
from workers.market_worker import MarketWorker
from market.base_provider import BaseMarketProvider


class TaskScheduler:
    """Планировщик фоновых задач."""

    def __init__(self, provider: BaseMarketProvider):
        self.scheduler = AsyncIOScheduler()
        self.market_worker = MarketWorker(provider)
        self._is_running = False

    def setup_jobs(self):
        """Настройка периодических задач."""
        # Задача сканирования для премиум пользователей (каждые 5 минут)
        self.scheduler.add_job(
            self._scan_premium_users,
            trigger=CronTrigger(minute="*/5"),
            id="scan_premium",
            name="Scan premium users",
            replace_existing=True,
        )

        # Задача сканирования для бесплатных пользователей (каждые 30 минут)
        self.scheduler.add_job(
            self._scan_free_users,
            trigger=CronTrigger(minute="*/30"),
            id="scan_free",
            name="Scan free users",
            replace_existing=True,
        )

        logger.info("Scheduler jobs configured")

    async def _scan_premium_users(self):
        """Сканирование для премиум пользователей."""
        if not self._is_running:
            return

        async with async_session_maker() as session:
            result = await session.execute(
                select(User).join(Subscription).where(
                    Subscription.plan == "premium",
                    Subscription.status == "active"
                )
            )
            users = result.scalars().all()

        for user in users:
            try:
                await self.market_worker.scan_for_user(user.id)
            except Exception as e:
                logger.error(f"Error scanning for premium user {user.id}: {e}")

    async def _scan_free_users(self):
        """Сканирование для бесплатных пользователей."""
        if not self._is_running:
            return

        async with async_session_maker() as session:
            result = await session.execute(
                select(User).outerjoin(Subscription).where(
                    (Subscription.id.is_(None)) | 
                    (Subscription.plan == "free")
                )
            )
            users = result.scalars().all()

        for user in users:
            try:
                await self.market_worker.scan_for_user(user.id)
            except Exception as e:
                logger.error(f"Error scanning for free user {user.id}: {e}")

    def start(self):
        """Запуск планировщика."""
        self._is_running = True
        self.setup_jobs()
        self.scheduler.start()
        logger.info("Scheduler started")

    def stop(self):
        """Остановка планировщика."""
        self._is_running = False
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")
