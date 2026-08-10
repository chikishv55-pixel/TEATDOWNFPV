from core.schemas import ItemStats


def calculate_liquidity_score(stats: ItemStats) -> float:
    """
    Расчет показателя ликвидности (0-10).

    Нормированный балл на основе:
    - volume_24h (0-4 балла);
    - volume_7d (0-3 балла);
    - spread (0-3 балла, чем меньше тем лучше).
    """
    score = 0.0

    # Объем за 24 часа (максимум 4 балла)
    if stats.volume_24h >= 100:
        score += 4.0
    elif stats.volume_24h >= 50:
        score += 3.0
    elif stats.volume_24h >= 20:
        score += 2.0
    elif stats.volume_24h >= 10:
        score += 1.0

    # Объем за 7 дней (максимум 3 балла)
    if stats.volume_7d >= 500:
        score += 3.0
    elif stats.volume_7d >= 200:
        score += 2.0
    elif stats.volume_7d >= 100:
        score += 1.0

    # Spread (максимум 3 балла, чем меньше тем лучше)
    if stats.spread is not None:
        if stats.spread <= 0.05:
            score += 3.0
        elif stats.spread <= 0.1:
            score += 2.0
        elif stats.spread <= 0.2:
            score += 1.0

    return round(min(score, 10.0), 1)


def is_liquid_item(
    volume_24h: int,
    volume_7d: int,
    min_volume_24h: int,
    min_volume_7d: int,
) -> bool:
    """Проверка достаточной ликвидности предмета."""
    return volume_24h >= min_volume_24h and volume_7d >= min_volume_7d


def check_price_outlier(price: float, median_price: float, threshold: float = 0.5) -> bool:
    """
    Проверка на выброс цены.

    Возвращает True, если цена подозрительно отличается от медианной.
    """
    if median_price <= 0:
        return True

    deviation = abs(price - median_price) / median_price
    return deviation > threshold
