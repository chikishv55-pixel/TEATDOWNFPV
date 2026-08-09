from aiogram import Bot
from aiogram.types import LabeledPrice, PreCheckoutQuery, Invoice
from core.logging import logger


class StarsPayment:
    """Обработка платежей через Telegram Stars."""

    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_invoice(
        self,
        chat_id: int,
        title: str = "Премиум подписка",
        description: str = "Оплата премиум-подписки на 1 месяц",
        payload: str = "premium_1month",
        provider_token: str = "",
        currency: str = "XTR",  # Telegram Stars
        prices: list[LabeledPrice] = None,
        start_parameter: str = "premium",
    ):
        """Отправка инвойса пользователю."""
        if prices is None:
            prices = [LabeledPrice(label="Premium 1 month", amount=1990)]  # 1990 Stars

        try:
            await self.bot.send_invoice(
                chat_id=chat_id,
                title=title,
                description=description,
                payload=payload,
                provider_token=provider_token,
                currency=currency,
                prices=prices,
                start_parameter=start_parameter,
            )
            logger.info(f"Invoice sent to {chat_id}")
        except Exception as e:
            logger.error(f"Error sending invoice to {chat_id}: {e}")
            raise

    async def process_pre_checkout(
        self, pre_checkout_query: PreCheckoutQuery
    ):
        """Обработка pre-checkout запроса."""
        try:
            await self.bot.answer_pre_checkout_query(
                pre_checkout_query_id=pre_checkout_query.id,
                ok=True,
            )
            logger.info(f"Pre-checkout approved for {pre_checkout_query.from_user.id}")
        except Exception as e:
            logger.error(f"Error processing pre-checkout: {e}")
            await self.bot.answer_pre_checkout_query(
                pre_checkout_query_id=pre_checkout_query.id,
                ok=False,
                error_message="Произошла ошибка при обработке платежа. Попробуйте позже.",
            )

    async def process_successful_payment(
        self, message, amount: int, currency: str, payload: str
    ):
        """Обработка успешного платежа."""
        try:
            # Здесь логика активации премиума
            logger.info(
                f"Payment successful: {amount} {currency}, payload: {payload}, "
                f"user: {message.from_user.id}"
            )

            # Отправляем подтверждение
            await message.answer(
                "✅ Оплата прошла успешно!\n\n"
                "Ваша премиум-подписка активирована.\n"
                "Теперь вам доступны:\n"
                "• До 20 фильтров\n"
                "• Обновление каждые 5 минут\n"
                "• Расширенная история сигналов\n\n"
                "Спасибо за покупку! 🎉"
            )
        except Exception as e:
            logger.error(f"Error processing successful payment: {e}")
