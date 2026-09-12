from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import Car
from bot.db.repository import CarFilters, list_cars
from bot.i18n import detect_language, t

router = Router(name="catalog")


def _format_car(car: Car) -> str:
    return (
        f"{car.make} {car.model} ({car.year}) — {car.price_eur}€\n"
        f"{car.mileage_km} km, {car.color}, {car.condition}"
    )


async def show_catalog(message: Message, session: AsyncSession, filters: CarFilters) -> None:
    lang = detect_language(message.text or "")
    cars = await list_cars(session, filters)

    if not cars:
        await message.answer(t("no_results", lang))
        return

    for car in cars:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=t("book", lang), callback_data=f"book:{car.id}")]
            ]
        )
        await message.answer(_format_car(car), reply_markup=keyboard)


@router.message(Command("catalog"))
async def handle_catalog(message: Message, session: AsyncSession) -> None:
    await show_catalog(message, session, CarFilters())
