import random
from typing import Optional
from market.base_provider import BaseMarketProvider
from core.schemas import ItemStats, Listing, Item
from core.logging import logger


class MockMarketProvider(BaseMarketProvider):
    """
    Mock-провайдер для разработки и тестирования.
    Генерирует реалистичные тестовые данные.
    """

    # Тестовые предметы для генерации
    MOCK_ITEMS = [
        "AK-47 | Redline (Field-Tested)",
        "AWP | Asiimov (Field-Tested)",
        "M4A4 | Howl (Minimal Wear)",
        "Karambit | Fade (Factory New)",
        "Glock-18 | Fade (Factory New)",
        "USP-S | Kill Confirmed (Minimal Wear)",
        "Desert Eagle | Blaze (Factory New)",
        "Sport Gloves | Pandora's Box (Field-Tested)",
        "★ Karambit | Doppler (Factory New)",
        "M9 Bayonet | Lore (Minimal Wear)",
    ]

    def __init__(self, fee_percent: float = 0.15):
        self._fee_percent = fee_percent

    @property
    def name(self) -> str:
        return "Mock"

    @property
    def fee_percent(self) -> float:
        return self._fee_percent

    async def fetch_item_stats(self, item: Item) -> ItemStats:
        """Генерирует случайную статистику для предмета."""
        logger.debug(f"Mock: fetching stats for {item.market_hash_name}")

        # Генерируем реалистичные цены
        base_price = random.uniform(500, 50000)
        median_7d = base_price * random.uniform(0.9, 1.1)
        median_24h = median_7d * random.uniform(0.95, 1.05)

        return ItemStats(
            avg_price_24h=median_24h * random.uniform(0.98, 1.02),
            median_price_24h=median_24h,
            avg_price_7d=median_7d * random.uniform(0.98, 1.02),
            median_price_7d=median_7d,
            min_price_24h=median_24h * random.uniform(0.85, 0.95),
            min_price_7d=median_7d * random.uniform(0.8, 0.95),
            volume_24h=random.randint(10, 500),
            volume_7d=random.randint(50, 2000),
            spread=random.uniform(0.02, 0.15),
            liquidity_score=random.uniform(3.0, 9.5),
        )

    async def fetch_listings(self, item: Item) -> list[Listing]:
        """Генерирует случайные лоты для предмета."""
        logger.debug(f"Mock: fetching listings for {item.market_hash_name}")

        base_price = random.uniform(500, 50000)
        num_listings = random.randint(5, 30)

        listings = []
        for i in range(num_listings):
            # Некоторые лоты могут быть выгодными
            discount = random.uniform(-0.1, 0.25)  # от -10% до +25% скидки
            price = base_price * (1 - discount)

            listings.append(
                Listing(
                    listing_id=f"mock_listing_{random.randint(10000, 99999)}",
                    price=round(price, 2),
                    currency="RUB",
                    seller=f"seller_{random.randint(1, 1000)}",
                    float_value=round(random.uniform(0.0, 1.0), 4),
                    url=f"https://mock.market/item/{item.market_hash_name}/{i}",
                )
            )

        return listings

    async def search_items(self, query: str) -> list[Item]:
        """Возвращает тестовые предметы."""
        logger.debug(f"Mock: searching for '{query}'")

        items = []
        for name in self.MOCK_ITEMS:
            if query.lower() in name.lower() or query == "":
                is_stattrak = "StatTrak" in name or random.random() < 0.2
                is_souvenir = "Souvenir" in name or random.random() < 0.05

                items.append(
                    Item(
                        market_hash_name=name,
                        app_id=730,
                        category="skins",
                        is_stattrak=is_stattrak,
                        is_souvenir=is_souvenir,
                        icon_url=f"https://mock.cdn/icons/{name.replace(' ', '_')}.png",
                    )
                )

        return items[:10]  # Ограничиваем количество
