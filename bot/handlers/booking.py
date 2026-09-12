from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.repository import book_car
from bot.i18n import detect_language, t

router = Router(name="booking")


async def handle_book_callback(callback: CallbackQuery, session: AsyncSession, car_id: int) -> None:
    if isinstance(callback.message, Message):
        lang = detect_language(callback.message.text or "")
    else:
        lang = detect_language("")
    booking = await book_car(
        session,
        car_id=car_id,
        telegram_user_id=callback.from_user.id,
        contact_name=callback.from_user.full_name,
    )

    if booking is None:
        await callback.answer(t("car_reserved", lang), show_alert=True)
        return

    await callback.answer(t("booking_confirmed", lang), show_alert=True)


@router.callback_query(F.data.startswith("book:"))
async def handle_book(callback: CallbackQuery, session: AsyncSession) -> None:
    car_id = int(callback.data.split(":", 1)[1])  # type: ignore[union-attr]
    await handle_book_callback(callback, session, car_id)
