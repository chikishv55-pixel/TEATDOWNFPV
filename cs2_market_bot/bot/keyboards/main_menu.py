from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_menu() -> InlineKeyboardMarkup:
    """Главное меню бота."""
    builder = InlineKeyboardBuilder()

    builder.button(text="🔎 Сканировать рынок", callback_data="scan_market")
    builder.button(text="⚙️ Мои фильтры", callback_data="my_filters")
    builder.button(text="📌 Последние сигналы", callback_data="last_signals")
    builder.button(text="💎 Премиум", callback_data="premium")
    builder.button(text="ℹ️ Помощь", callback_data="help")

    builder.adjust(1)
    return builder.as_markup()


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой «Назад»."""
    builder = InlineKeyboardBuilder()
    builder.button(text="« Назад", callback_data="back_to_menu")
    builder.adjust(1)
    return builder.as_markup()


def get_filters_menu_keyboard() -> InlineKeyboardMarkup:
    """Меню управления фильтрами."""
    builder = InlineKeyboardBuilder()

    builder.button(text="➕ Создать фильтр", callback_data="filter_create")
    builder.button(text="📋 Мои фильтры", callback_data="filter_list")
    builder.button(text="« Назад", callback_data="back_to_menu")

    builder.adjust(1)
    return builder.as_markup()
