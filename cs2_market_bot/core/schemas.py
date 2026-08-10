from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class ItemStats(BaseModel):
    """Статистика предмета."""
    avg_price_24h: Optional[float] = None
    median_price_24h: Optional[float] = None
    avg_price_7d: Optional[float] = None
    median_price_7d: Optional[float] = None
    min_price_24h: Optional[float] = None
    min_price_7d: Optional[float] = None
    volume_24h: int = 0
    volume_7d: int = 0
    spread: Optional[float] = None
    liquidity_score: float = 0.0


class Listing(BaseModel):
    """Лот на рынке."""
    listing_id: str
    price: float
    currency: str = "RUB"
    seller: Optional[str] = None
    float_value: Optional[float] = None
    url: Optional[str] = None


class Item(BaseModel):
    """Предмет."""
    market_hash_name: str
    app_id: int = 730
    category: Literal["skins", "cases", "stickers", "capsules", "agents", "keys"] = "skins"
    is_stattrak: bool = False
    is_souvenir: bool = False
    icon_url: Optional[str] = None


class SignalData(BaseModel):
    """Данные сигнала."""
    item_name: str
    price: float
    average_price_7d: float
    discount_percent: float
    potential_profit: Optional[float] = None
    liquidity_score: float
    volume_24h: int
    url: Optional[str] = None


class UserFilter(BaseModel):
    """Фильтр пользователя."""
    min_discount_percent: float = Field(default=10.0, ge=0, le=100)
    min_volume_24h: int = Field(default=10, ge=0)
    min_volume_7d: int = Field(default=50, ge=0)
    min_price: float = Field(default=0.0, ge=0)
    max_price: float = Field(default=100000.0, ge=0)
    include_stattrak: bool = True
    include_souvenir: bool = True
    categories: list[str] = ["skins", "cases", "stickers", "capsules", "agents", "keys"]
    min_liquidity_score: float = Field(default=5.0, ge=0, le=10)
    max_spread: float = Field(default=0.3, ge=0, le=1)
