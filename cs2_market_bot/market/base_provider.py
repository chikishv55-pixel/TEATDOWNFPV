from abc import ABC, abstractmethod
from typing import Optional
from core.schemas import ItemStats, Listing, Item


class BaseMarketProvider(ABC):
    """Абстрактный класс провайдера рыночных данных."""

    @abstractmethod
    async def fetch_item_stats(self, item: Item) -> ItemStats:
        """
        Получить статистику предмета.

        Args:
            item: Предмет для получения статистики.

        Returns:
            ItemStats: Статистика предмета.
        """
        pass

    @abstractmethod
    async def fetch_listings(self, item: Item) -> list[Listing]:
        """
        Получить активные лоты для предмета.

        Args:
            item: Предмет для получения лотов.

        Returns:
            list[Listing]: Список активных лотов.
        """
        pass

    @abstractmethod
    async def search_items(self, query: str) -> list[Item]:
        """
        Поиск предметов по запросу.

        Args:
            query: Поисковый запрос.

        Returns:
            list[Item]: Список найденных предметов.
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Название провайдера."""
        pass

    @property
    @abstractmethod
    def fee_percent(self) -> float:
        """Комиссия площадки."""
        pass
