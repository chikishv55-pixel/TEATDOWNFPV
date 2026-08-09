from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select

from core.models import User, Subscription
from core.database import async_session_maker


class AuthMiddleware(BaseMiddleware):
    """Middleware для авторизации пользователя."""

    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        # Получаем telegram_id из события
        if isinstance(event, Message):
            telegram_id = str(event.from_user.id)
            username = event.from_user.username
        elif isinstance(event, CallbackQuery):
            telegram_id = str(event.from_user.id)
            username = event.from_user.username
        else:
            return await handler(event, data)

        # Проверяем наличие пользователя в БД
        async with async_session_maker() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                # Создаем нового пользователя
                user = User(telegram_id=telegram_id, username=username)
                session.add(user)
                await session.flush()

            # Добавляем пользователя в контекст
            data["user"] = user

            # Проверяем подписку
            result = await session.execute(
                select(Subscription).where(Subscription.user_id == user.id)
            )
            subscription = result.scalar_one_or_none()

            if subscription:
                data["subscription"] = subscription
                data["is_premium"] = subscription.plan == "premium"
            else:
                data["is_premium"] = False

        return await handler(event, data)
