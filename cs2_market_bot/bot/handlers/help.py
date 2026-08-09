from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from bot.keyboards import get_back_keyboard

router = Router()


@router.callback_query(F.data == "help")
async def help_callback(callback: CallbackQuery):
    """Показать справку."""
    help_text = (
        "ℹ️ *Помощь*\n\n"
        "Этот бот помогает находить выгодные лоты на рынке скинов CS2.\n\n"
        "*Как это работает:*\n"
        "1. Бот сканирует рынок и анализирует цены\n"
        "2. Сравнивает текущие цены со средней за 7 дней\n"
        "3. Находит лоты со скидкой от заданного процента\n"
        "4. Отправляет уведомления о выгодных предложениях\n\n"
        "*Фильтры:*\n"
        "Вы можете настроить фильтры для поиска:\n"
        "- Минимальная скидка (%)\n"
        "- Объем продаж (24ч / 7д)\n"
        "- Диапазон цен\n"
        "- Категории предметов\n"
        "- Ликвидность\n\n"
        "*Тарифы:*\n"
        "🆓 *Free*: 3 фильтра, обновление 30 мин\n"
        "💎 *Premium*: 20 фильтров, обновление 5 мин\n\n"
        "⚠️ *Дисклеймер*:\n"
        "Бот предоставляет аналитику, а не финансовый совет. "
        "Торговля скинами связана с рисками."
    )

    await callback.message.edit_text(
        text=help_text,
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.message(F.text == "/help")
async def help_command(message: Message):
    """Команда /help."""
    help_text = (
        "ℹ️ *Помощь*\n\n"
        "Этот бот помогает находить выгодные лоты на рынке скинов CS2.\n\n"
        "*Команды:*\n"
        "/start - Главное меню\n"
        "/scan - Запустить сканирование\n"
        "/filters - Настроить фильтры\n"
        "/signals - Последние сигналы\n"
        "/premium - Информация о премиуме\n"
        "/help - Эта справка\n\n"
        "⚠️ Бот предоставляет аналитику, а не финансовый совет."
    )

    await message.answer(
        text=help_text,
        parse_mode="Markdown",
    )
