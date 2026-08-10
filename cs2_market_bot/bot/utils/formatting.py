def format_price(price: float, currency: str = "RUB") -> str:
    """Форматирование цены."""
    if currency == "RUB":
        return f"{price:,.0f} ₽"
    elif currency == "USD":
        return f"${price:,.2f}"
    return f"{price:,.2f} {currency}"


def format_discount(discount: float) -> str:
    """Форматирование скидки."""
    sign = "+" if discount > 0 else ""
    return f"{sign}{discount:.1f}%"


def format_liquidity(score: float) -> str:
    """Форматирование показателя ликвидности."""
    if score >= 8.0:
        emoji = "🟢"
    elif score >= 5.0:
        emoji = "🟡"
    else:
        emoji = "🔴"
    return f"{emoji} {score}/10"


def truncate_text(text: str, max_length: int = 50) -> str:
    """Обрезка текста до максимальной длины."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
