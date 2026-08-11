import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional
from datetime import datetime, timedelta, timezone

from market.base_provider import BaseMarketProvider
from core.models import Item as DBItem, MarketStats, Listing as DBListing, Signal, Filter, User
from core.schemas import Item, ItemStats, Listing, UserFilter
from market.pricing import (
    calculate_discount_percent,
    calculate_potential_profit,
    generate_signal_hash,
    is_worthwhile_signal,
)
from market.liquidity import calculate_liquidity_score, check_price_outlier
from core.config import settings
from core.logging import logger


class MarketScanner:
    """Сервис сканирования рынка для поиска выгодных лотов."""

    def __init__(self, provider: BaseMarketProvider, db_session: AsyncSession):
        self.provider = provider
        self.db = db_session
        self.fee_percent = settings.fee_percent

    async def scan_item(self, item: Item) -> list[Signal]:
        """
        Сканирование одного предмета на наличие выгодных лотов.

        Returns:
            list[Signal]: Список созданных сигналов.
        """
        signals = []

        # Получаем статистику предмета
        try:
            stats = await self.provider.fetch_item_stats(item)
        except Exception as e:
            logger.error(f"Error fetching stats for {item.market_hash_name}: {e}")
            return signals

        # Получаем активные лоты
        try:
            listings = await self.provider.fetch_listings(item)
        except Exception as e:
            logger.error(f"Error fetching listings for {item.market_hash_name}: {e}")
            return signals

        # Сохраняем или обновляем предмет в БД
        db_item = await self._get_or_create_item(item)

        # Сохраняем статистику
        await self._update_market_stats(db_item.id, stats)

        # Проверяем каждый лот
        for listing in listings:
            signal = await self._check_listing(db_item, listing, stats)
            if signal:
                signals.append(signal)

        return signals

    async def _get_or_create_item(self, item: Item) -> DBItem:
        """Получить или создать предмет в БД."""
        result = await self.db.execute(
            select(DBItem).where(DBItem.market_hash_name == item.market_hash_name)
        )
        db_item = result.scalar_one_or_none()

        if not db_item:
            db_item = DBItem(
                market_hash_name=item.market_hash_name,
                app_id=item.app_id,
                category=item.category,
                is_stattrak=item.is_stattrak,
                is_souvenir=item.is_souvenir,
                icon_url=item.icon_url,
            )
            self.db.add(db_item)
            await self.db.flush()

        return db_item

    async def _update_market_stats(self, item_id: int, stats: ItemStats):
        """Обновить статистику рынка для предмета."""
        result = await self.db.execute(
            select(MarketStats).where(MarketStats.item_id == item_id)
        )
        db_stats = result.scalar_one_or_none()

        liquidity_score = calculate_liquidity_score(stats)

        if db_stats:
            db_stats.avg_price_24h = stats.avg_price_24h
            db_stats.median_price_24h = stats.median_price_24h
            db_stats.avg_price_7d = stats.avg_price_7d
            db_stats.median_price_7d = stats.median_price_7d
            db_stats.min_price_24h = stats.min_price_24h
            db_stats.min_price_7d = stats.min_price_7d
            db_stats.volume_24h = stats.volume_24h
            db_stats.volume_7d = stats.volume_7d
            db_stats.spread = stats.spread
            db_stats.liquidity_score = liquidity_score
            db_stats.updated_at = datetime.now(timezone.utc)
        else:
            db_stats = MarketStats(
                item_id=item_id,
                avg_price_24h=stats.avg_price_24h,
                median_price_24h=stats.median_price_24h,
                avg_price_7d=stats.avg_price_7d,
                median_price_7d=stats.median_price_7d,
                min_price_24h=stats.min_price_24h,
                min_price_7d=stats.min_price_7d,
                volume_24h=stats.volume_24h,
                volume_7d=stats.volume_7d,
                spread=stats.spread,
                liquidity_score=liquidity_score,
            )
            self.db.add(db_stats)

        await self.db.flush()

    async def _check_listing(
        self, db_item: DBItem, listing: Listing, stats: ItemStats
    ) -> Optional[Signal]:
        """Проверить лот на соответствие критериям выгоды."""
        # Используем медианную цену за 7 дней как базовую
        average_price_7d = stats.median_price_7d
        if not average_price_7d or average_price_7d <= 0:
            average_price_7d = stats.avg_price_7d

        if not average_price_7d or average_price_7d <= 0:
            return None

        # Проверка на выброс цены (анти-фрод)
        if check_price_outlier(listing.price, average_price_7d, threshold=0.6):
            logger.debug(
                f"Price outlier detected for {db_item.market_hash_name}: "
                f"{listing.price} vs {average_price_7d}"
            )
            return None

        # Расчет показателей
        discount_percent = calculate_discount_percent(average_price_7d, listing.price)
        potential_profit = calculate_potential_profit(
            average_price_7d, listing.price, self.fee_percent
        )
        liquidity_score = stats.liquidity_score

        # Получаем все активные фильтры пользователей
        result = await self.db.execute(
            select(Filter).where(
                and_(
                    Filter.is_active == True,
                )
            )
        )
        filters = result.scalars().all()

        # Проверяем соответствие хотя бы одному фильтру
        matched_filter = None
        for flt in filters:
            user_filter = UserFilter(
                min_discount_percent=flt.min_discount_percent,
                min_volume_24h=flt.min_volume_24h,
                min_volume_7d=flt.min_volume_7d,
                min_price=flt.min_price,
                max_price=flt.max_price,
                include_stattrak=flt.include_stattrak,
                include_souvenir=flt.include_souvenir,
                categories=flt.categories.split(",") if flt.categories else [],
                min_liquidity_score=flt.min_liquidity_score,
                max_spread=flt.max_spread,
            )

            if self._matches_filter(
                discount_percent,
                stats.volume_24h,
                stats.volume_7d,
                listing.price,
                liquidity_score,
                stats.spread,
                user_filter,
                db_item,
            ):
                matched_filter = flt
                break

        if not matched_filter:
            return None

        # Проверка на дубликат сигнала
        timestamp = int(time.time())
        signal_hash = generate_signal_hash(db_item.id, listing.listing_id, listing.price, timestamp)

        # Проверяем, не было ли такого сигнала недавно
        window_hours = settings.signal_duplicate_window_hours
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=window_hours)

        result = await self.db.execute(
            select(Signal).where(
                and_(
                    Signal.signal_hash == signal_hash,
                    Signal.created_at >= cutoff_time,
                )
            )
        )
        existing_signal = result.scalar_one_or_none()

        if existing_signal:
            logger.debug(f"Duplicate signal detected: {signal_hash}")
            return None

        # Создаем сигнал
        signal = Signal(
            item_id=db_item.id,
            listing_id=listing.listing_id,
            price=listing.price,
            average_price_7d=average_price_7d,
            discount_percent=discount_percent,
            potential_profit=potential_profit,
            liquidity_score=liquidity_score,
            signal_hash=signal_hash,
        )
        self.db.add(signal)
        await self.db.flush()

        logger.info(
            f"Signal created: {db_item.market_hash_name} - "
            f"{discount_percent}% discount, profit: {potential_profit}"
        )

        return signal

    def _matches_filter(
        self,
        discount_percent: float,
        volume_24h: int,
        volume_7d: int,
        price: float,
        liquidity_score: float,
        spread: float | None,
        user_filter: UserFilter,
        item: DBItem,
    ) -> bool:
        """Проверка соответствия лота фильтру пользователя."""
        # Категории
        if item.category not in user_filter.categories:
            return False

        # StatTrak / Souvenir
        if item.is_stattrak and not user_filter.include_stattrak:
            return False
        if item.is_souvenir and not user_filter.include_souvenir:
            return False

        # Основные критерии
        return is_worthwhile_signal(
            discount_percent=discount_percent,
            volume_24h=volume_24h,
            volume_7d=volume_7d,
            listing_price=price,
            liquidity_score=liquidity_score,
            spread=spread,
            min_discount=user_filter.min_discount_percent,
            min_volume_24h=user_filter.min_volume_24h,
            min_volume_7d=user_filter.min_volume_7d,
            min_price=user_filter.min_price,
            max_price=user_filter.max_price,
            min_liquidity=user_filter.min_liquidity_score,
            max_spread=user_filter.max_spread,
        )

    async def get_signals_for_user(
        self, user_id: int, limit: int = 10
    ) -> list[Signal]:
        """Получить последние сигналы для пользователя."""
        result = await self.db.execute(
            select(Signal)
            .where(Signal.user_id == user_id)
            .order_by(Signal.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_unsent_signals(
        self, user_id: int, limit: int = 10
    ) -> list[tuple[Signal, DBItem]]:
        """Получить неотправленные сигналы для пользователя."""
        result = await self.db.execute(
            select(Signal, DBItem)
            .join(DBItem, Signal.item_id == DBItem.id)
            .where(
                and_(
                    Signal.sent_at.is_(None),
                    Signal.user_id == user_id,
                )
            )
            .order_by(Signal.created_at.desc())
            .limit(limit)
        )
        return result.all()

    async def mark_signal_sent(self, signal_id: int):
        """Отметить сигнал как отправленный."""
        result = await self.db.execute(
            select(Signal).where(Signal.id == signal_id)
        )
        signal = result.scalar_one_or_none()
        if signal:
            signal.sent_at = datetime.now(timezone.utc)
            await self.db.flush()
