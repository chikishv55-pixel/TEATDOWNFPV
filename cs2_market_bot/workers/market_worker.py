import asyncio
from sqlalchemy import select
from typing import List

from market.base_provider import BaseMarketProvider
from market.scanner import MarketScanner
from core.models import User, Filter, Item as DBItem
from core.schemas import Item
from core.database import async_session_maker
from core.logging import logger


class MarketWorker:
    """Воркер для периодического сканирования рынка."""

    def __init__(self, provider: BaseMarketProvider):
        self.provider = provider

    async def scan_for_user(self, user_id: int):
        """Сканирование рынка для конкретного пользователя."""
        async with async_session_maker() as session:
            scanner = MarketScanner(self.provider, session)

            # Получаем активные фильтры пользователя
            result = await session.execute(
                select(Filter).where(
                    Filter.user_id == user_id,
                    Filter.is_active == True
                )
            )
            filters = result.scalars().all()

            if not filters:
                logger.debug(f"No active filters for user {user_id}")
                return

            # Получаем предметы для сканирования (из популярных)
            items_to_scan = await self._get_items_to_scan(session, filters)

            signals_found = 0
            for item in items_to_scan:
                signals = await scanner.scan_item(item)
                signals_found += len(signals)

            logger.info(f"User {user_id}: scanned {len(items_to_scan)} items, found {signals_found} signals")

    async def _get_items_to_scan(
        self, session, filters: List[Filter]
    ) -> List[Item]:
        """Получить список предметов для сканирования."""
        # Собираем категории из всех фильтров
        categories = set()
        for flt in filters:
            if flt.categories:
                categories.update(flt.categories.split(","))

        # Получаем предметы из базы или создаем новые через провайдера
        result = await session.execute(
            select(DBItem).where(DBItem.category.in_(list(categories)))
        )
        db_items = result.scalars().all()

        items = []
        for db_item in db_items[:50]:  # Ограничиваем количество
            items.append(
                Item(
                    market_hash_name=db_item.market_hash_name,
                    app_id=db_item.app_id,
                    category=db_item.category,
                    is_stattrak=db_item.is_stattrak,
                    is_souvenir=db_item.is_souvenir,
                    icon_url=db_item.icon_url,
                )
            )

        # Если предметов мало, запрашиваем у провайдера
        if len(items) < 10:
            try:
                new_items = await self.provider.search_items("")
                items.extend(new_items[:20])
            except Exception as e:
                logger.error(f"Error fetching items from provider: {e}")

        return items

    async def send_notifications(self, user_id: int):
        """Отправка уведомлений о новых сигналах."""
        async with async_session_maker() as session:
            # Здесь будет логика отправки уведомлений
            # Для MVP просто логируем
            logger.info(f"Sending notifications to user {user_id}")
