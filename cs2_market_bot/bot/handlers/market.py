from aiogram import Router, F
from aiogram.types import CallbackQuery
from bot.keyboards import get_back_keyboard, get_filters_menu_keyboard
from core.logging import logger

router = Router()


@router.callback_query(F.data == "scan_market")
async def scan_market_callback(callback: CallbackQuery):
    """Обработчик кнопки 'Сканировать рынок'."""
    await callback.answer("🔎 Запуск сканирования рынка...", show_alert=False)
    
    scan_text = (
        "🔎 *Сканирование рынка*\\n\\n"
        "Бот анализирует текущие предложения на рынке CS2...\\n\\n"
        "⏳ Пожалуйста, подождите. Результаты появятся здесь, "
        "как только будут найдены выгодные лоты, соответствующие вашим фильтрам.\\n\\n"
        "_Совет: Настройте фильтры в разделе 'Мои фильтры' для более точного поиска._"
    )
    
    await callback.message.edit_text(
        text=scan_text,
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    logger.info(f"User {callback.from_user.id} started market scan")


@router.callback_query(F.data == "my_filters")
async def my_filters_callback(callback: CallbackQuery):
    """Обработчик кнопки 'Мои фильтры'."""
    await callback.answer("⚙️ Открытие меню фильтров...", show_alert=False)
    
    filters_text = (
        "⚙️ *Управление фильтрами*\\n\\n"
        "Здесь вы можете создавать и настраивать фильтры для поиска выгодных лотов.\\n\\n"
        "Фильтры позволяют искать предметы по:\\n"
        "• Минимальной скидке (%)\\n"
        "• Объему продаж\\n"
        "• Диапазону цен\\n"
        "• Категории предметов\\n"
        "• Ликвидности\\n\\n"
        "Выберите действие ниже:"
    )
    
    await callback.message.edit_text(
        text=filters_text,
        reply_markup=get_filters_menu_keyboard(),
        parse_mode="Markdown",
    )
    logger.info(f"User {callback.from_user.id} opened filters menu")


@router.callback_query(F.data == "filter_create")
async def filter_create_callback(callback: CallbackQuery):
    """Обработчик кнопки 'Создать фильтр'."""
    await callback.answer("➕ Создание нового фильтра", show_alert=True)
    
    create_text = (
        "➕ *Создание фильтра*\\n\\n"
        "Для создания фильтра отправьте команду:\\n"
        "`/newfilter`\\n\\n"
        "Бот предложит вам пошагово настроить параметры:\\n"
        "1. Название фильтра\\n"
        "2. Минимальная скидка (%)\\n"
        "3. Минимальный объем продаж за 24ч\\n"
        "4. Диапазон цен (мин-макс)\\n"
        "5. Категории предметов\\n\\n"
        "Нажмите 'Назад' для возврата в меню."
    )
    
    await callback.message.edit_text(
        text=create_text,
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    logger.info(f"User {callback.from_user.id} wants to create filter")


@router.callback_query(F.data == "filter_list")
async def filter_list_callback(callback: CallbackQuery):
    """Обработчик кнопки 'Мои фильтры' (список)."""
    from sqlalchemy import select
    from core.models import Filter
    from core.database import async_session_maker
    
    telegram_id = str(callback.from_user.id)
    
    async with async_session_maker() as session:
        result = await session.execute(
            select(Filter).where(Filter.user_id == telegram_id)
        )
        filters = result.scalars().all()
    
    if not filters:
        no_filters_text = (
            "📋 *Ваши фильтры*\\n\\n"
            "У вас пока нет активных фильтров.\\n\\n"
            "Создайте первый фильтр, чтобы получать персонализированные сигналы!\\n\\n"
            "Нажмите '➕ Создать фильтр' ниже."
        )
        await callback.message.edit_text(
            text=no_filters_text,
            reply_markup=get_filters_menu_keyboard(),
            parse_mode="Markdown",
        )
        await callback.answer()
        return
    
    filters_text = "📋 *Ваши активные фильтры:*\\n\\n"
    for i, f in enumerate(filters, 1):
        status = "✅" if f.is_active else "❌"
        filters_text += (
            f"{status} *{i}. {f.name}*\\n"
            f"   Скидка: от {f.min_discount}%\\n"
            f"   Продажи 24ч: от {f.min_volume_24h}\\n"
            f"   Цена: {f.min_price} - {f.max_price} ₽\\n\\n"
        )
    
    filters_text += f"_Всего фильтров: {len(filters)}_"
    
    await callback.message.edit_text(
        text=filters_text,
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()
    logger.info(f"User {callback.from_user.id} viewed filters list")
