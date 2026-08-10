from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base


class User(Base):
    """Таблица пользователей."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(String(50), unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=True)
    is_premium = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    filters = relationship("Filter", back_populates="user", cascade="all, delete-orphan")
    signals = relationship("Signal", back_populates="user", cascade="all, delete-orphan")
    subscription = relationship("Subscription", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Filter(Base):
    """Таблица фильтров пользователя."""
    __tablename__ = "filters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    min_discount_percent = Column(Float, default=10.0)
    min_volume_24h = Column(Integer, default=10)
    min_volume_7d = Column(Integer, default=50)
    min_price = Column(Float, default=0.0)
    max_price = Column(Float, default=100000.0)
    include_stattrak = Column(Boolean, default=True)
    include_souvenir = Column(Boolean, default=True)
    categories = Column(Text, default="skins,cases,stickers,capsules,agents,keys")
    min_liquidity_score = Column(Float, default=5.0)
    max_spread = Column(Float, default=0.3)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="filters")


class Item(Base):
    """Таблица предметов."""
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    market_hash_name = Column(String(255), nullable=False, index=True)
    app_id = Column(Integer, default=730)
    category = Column(String(50), default="skins")
    is_stattrak = Column(Boolean, default=False)
    is_souvenir = Column(Boolean, default=False)
    icon_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    stats = relationship("MarketStats", back_populates="item", uselist=False, cascade="all, delete-orphan")
    listings = relationship("Listing", back_populates="item", cascade="all, delete-orphan")
    signals = relationship("Signal", back_populates="item", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_items_category_stattrak", "category", "is_stattrak"),
    )


class MarketStats(Base):
    """Таблица статистики рынка."""
    __tablename__ = "market_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False, unique=True)
    source = Column(String(50), default="steam")
    avg_price_24h = Column(Float, nullable=True)
    median_price_24h = Column(Float, nullable=True)
    avg_price_7d = Column(Float, nullable=True)
    median_price_7d = Column(Float, nullable=True)
    min_price_24h = Column(Float, nullable=True)
    min_price_7d = Column(Float, nullable=True)
    volume_24h = Column(Integer, default=0)
    volume_7d = Column(Integer, default=0)
    spread = Column(Float, nullable=True)
    liquidity_score = Column(Float, default=0.0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    item = relationship("Item", back_populates="stats")


class Listing(Base):
    """Таблица активных лотов."""
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    source = Column(String(50), default="steam")
    listing_id = Column(String(100), nullable=False, index=True)
    price = Column(Float, nullable=False)
    currency = Column(String(10), default="RUB")
    seller = Column(String(100), nullable=True)
    float_value = Column(Float, nullable=True)
    is_stattrak = Column(Boolean, default=False)
    is_souvenir = Column(Boolean, default=False)
    url = Column(String(500), nullable=True)
    found_at = Column(DateTime(timezone=True), server_default=func.now())

    item = relationship("Item", back_populates="listings")


class Signal(Base):
    """Таблица сигналов."""
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    listing_id = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    price = Column(Float, nullable=False)
    average_price_7d = Column(Float, nullable=False)
    discount_percent = Column(Float, nullable=False)
    potential_profit = Column(Float, nullable=True)
    liquidity_score = Column(Float, nullable=True)
    signal_hash = Column(String(64), nullable=False, index=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    item = relationship("Item", back_populates="signals")
    user = relationship("User", back_populates="signals")


class Subscription(Base):
    """Таблица подписок."""
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    plan = Column(String(20), default="free")
    status = Column(String(20), default="active")
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="subscription")


class RateLimit(Base):
    """Таблица rate limiting."""
    __tablename__ = "rate_limits"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)
    last_used_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_rate_limits_user_action", "user_id", "action", unique=True),
    )
