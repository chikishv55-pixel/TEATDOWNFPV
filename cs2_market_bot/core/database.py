from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from core.config import settings


engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Базовый класс для всех ORM моделей."""
    pass


async def get_db() -> AsyncSession:
    """Dependency для получения сессии БД."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Инициализация БД - создание таблиц."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Закрытие подключения к БД."""
    await engine.dispose()
