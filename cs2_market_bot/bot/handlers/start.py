from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards import get_main_menu
from core.models import User
from core.database import async_session_maker
from sqlalchemy import select
from core.logging import logger

router = Router()


@router.message(F.text == "/start")
async def cmd_start(message: Message):
    """Обработчик команды /start."""
    telegram_id = str(message.from_user.id)
    username = message.from_user.username

    # Регистрируем пользователя в БД
    async with async_session_maker() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            user = User(telegram_id=telegram_id, username=username)
            session.add(user)
            await session.flush()
            logger.info(f"New user registered: {telegram_id} ({username})")
        else:
            user.username = username
            await session.flush()

    welcome_text = (
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "Я бот для поиска выгодных лотов на рынке скинов CS2.\n\n"
        "Я отслеживаю рыночные цены и нахожу предметы, которые продаются "
        "ниже их расчетной стоимости.\n\n"
        "⚠️ *Дисклеймер*: Бот предоставляет аналитику, а не финансовый совет. "
        "Торговля скинами связана с рисками."
    )

    await message.answer(
        text=welcome_text,
        reply_markup=get_main_menu(),
        parse_mode="Markdown",
    )


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    """Возврат в главное меню."""
    await callback.message.edit_text(
        text="🏠 Главное меню:",
        reply_markup=get_main_menu(),
    )
    await callback.answer()
