from core.schemas import ItemStats, Listing, Item
from core.config import settings


def calculate_discount_percent(average_price_7d: float, listing_price: float) -> float:
    """
    Расчет процента скидки.

    discount_percent = (average_price_7d - listing_price) / average_price_7d * 100
    """
    if average_price_7d <= 0:
        return 0.0

    discount = ((average_price_7d - listing_price) / average_price_7d) * 100
    return round(discount, 2)


def calculate_potential_profit(average_price_7d: float, listing_price: float, fee_percent: float) -> float:
    """
    Расчет потенциальной прибыли после комиссии.

    estimated_net_after_sale = average_price_7d * (1 - fee_percent)
    potential_profit = estimated_net_after_sale - listing_price
    """
    estimated_net = average_price_7d * (1 - fee_percent)
    profit = estimated_net - listing_price
    return round(profit, 2)


def calculate_liquidity_score(stats: ItemStats) -> float:
    """
    Расчет показателя ликвидности.

    Нормированный балл на основе:
    - volume_24h;
    - volume_7d;
    - spread;
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


def is_worthwhile_signal(
    discount_percent: float,
    volume_24h: int,
    volume_7d: int,
    listing_price: float,
    liquidity_score: float,
    spread: float | None,
    min_discount: float,
    min_volume_24h: int,
    min_volume_7d: int,
    min_price: float,
    max_price: float,
    min_liquidity: float,
    max_spread: float,
) -> bool:
    """
    Проверка, является ли сигнал выгодным по всем критериям.
    """
    if discount_percent < min_discount:
        return False

    if volume_24h < min_volume_24h:
        return False

    if volume_7d < min_volume_7d:
        return False

    if listing_price < min_price or listing_price > max_price:
        return False

    if liquidity_score < min_liquidity:
        return False

    if spread is not None and spread > max_spread:
        return False

    return True


def generate_signal_hash(item_id: int, listing_id: str, price: float, timestamp: int) -> str:
    """
    Генерация хэша сигнала для предотвращения дубликатов.

    hash = sha256(item_id + listing_id + price + timestamp)
    """
    import hashlib

    data = f"{item_id}:{listing_id}:{price}:{timestamp}"
    return hashlib.sha256(data.encode()).hexdigest()
