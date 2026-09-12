from unittest.mock import AsyncMock, MagicMock

from aiogram.types import Message

from bot.db.models import Car
from bot.handlers.booking import handle_book_callback


def _make_callback() -> MagicMock:
    callback = MagicMock()
    callback.message = MagicMock(spec=Message)
    callback.message.text = "привет"
    callback.from_user.id = 42
    callback.from_user.full_name = "Alice"
    callback.answer = AsyncMock()
    return callback


async def test_handle_book_callback_confirms_booking(db_session):
    car = Car(
        make="BMW", model="X5", year=2019, mileage_km=45000, color="black",
        is_new=False, owners_count=2, condition="good", price_eur=28000,
        description="BMW X5", status="available",
    )
    db_session.add(car)
    await db_session.commit()
    callback = _make_callback()

    await handle_book_callback(callback, db_session, car.id)

    callback.answer.assert_awaited_once()
    assert "принята" in callback.answer.call_args.args[0]


async def test_handle_book_callback_rejects_already_reserved(db_session):
    car = Car(
        make="BMW", model="X5", year=2019, mileage_km=45000, color="black",
        is_new=False, owners_count=2, condition="good", price_eur=28000,
        description="BMW X5", status="reserved",
    )
    db_session.add(car)
    await db_session.commit()
    callback = _make_callback()

    await handle_book_callback(callback, db_session, car.id)

    callback.answer.assert_awaited_once()
    assert "забронирован" in callback.answer.call_args.args[0]
