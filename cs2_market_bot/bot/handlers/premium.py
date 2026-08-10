from aiogram import Router, F
from aiogram.types import CallbackQuery
from bot.keyboards import get_back_keyboard
from core.config import settings

router = Router()


@router.callback_query(F.data == "premium")
async def premium_callback(callback: CallbackQuery):
    """Информация о премиуме."""
    premium_text = (
        "💎 *Премиум подписка*\n\n"
        "Получите максимум от бота с премиум-подпиской!\n\n"
        "*Сравнение тарифов:*\n\n"
        "🆓 *Free:*\n"
        f"• До {settings.max_free_filters} активных фильтров\n"
        f"• Обновление каждые {settings.free_scan_interval_minutes} мин\n"
        f"• До {settings.max_free_signals} последних сигналов\n"
        "• Базовые фильтры\n\n"
        "💎 *Premium:*\n"
        f"• До {settings.max_premium_filters} активных фильтров\n"
        f"• Обновление каждые {settings.premium_scan_interval_minutes} мин\n"
        f"• До {settings.max_premium_signals} сигналов\n"
        "• Расширенные фильтры\n"
        "• История за 7 дней\n"
        "• Приоритетная поддержка\n\n"
        "*Цена:*\n"
        "199 RUB/месяц или 1990 Stars\n\n"
        "Для оплаты нажмите кнопку ниже."
    )

    await callback.message.edit_text(
        text=premium_text,
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()
