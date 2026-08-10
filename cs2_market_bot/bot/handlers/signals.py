from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select, and_
from bot.keyboards import get_back_keyboard
from core.models import Signal, Item, User
from core.database import async_session_maker
from core.logging import logger
from datetime import datetime

router = Router()


@router.callback_query(F.data == "last_signals")
async def signals_callback(callback: CallbackQuery):
    """Показать последние сигналы."""
    telegram_id = str(callback.from_user.id)

    async with async_session_maker() as session:
        # Получаем пользователя
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            await callback.answer("Пользователь не найден. Нажмите /start", show_alert=True)
            return

        # Получаем последние сигналы
        result = await session.execute(
            select(Signal, Item)
            .join(Item, Signal.item_id == Item.id)
            .order_by(Signal.created_at.desc())
            .limit(10)
        )
        signals_with_items = result.all()

    if not signals_with_items:
        no_signals_text = (
            "📌 *Последние сигналы*\n\n"
            "Пока нет найденных сигналов.\n\n"
            "Бот продолжает сканировать рынок. "
            "Как только появятся выгодные лоты, вы получите уведомление!"
        )
        await callback.message.edit_text(
            text=no_signals_text,
            reply_markup=get_back_keyboard(),
            parse_mode="Markdown",
        )
        await callback.answer()
        return

    # Формируем сообщение с сигналами
    signals_text = "📌 *Последние сигналы*\n\n"

    for signal, item in signals_with_items[:10]:
        sent_status = "✅" if signal.sent_at else "⏳"
        signals_text += (
            f"{sent_status} *{item.market_hash_name}*\n"
            f"💰 Цена: {signal.price:.0f} ₽\n"
            f"📊 Средняя за 7д: {signal.average_price_7d:.0f} ₽\n"
            f"🔻 Скидка: {signal.discount_percent:.1f}%\n"
            f"💵 Прибыль: ~{signal.potential_profit:.0f} ₽\n"
            f"📈 Ликвидность: {signal.liquidity_score}/10\n\n"
        )

    signals_text += "_Отправлено ботом для поиска выгодных лотов CS2_"

    await callback.message.edit_text(
        text=signals_text,
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()
