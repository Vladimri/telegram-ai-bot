from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock

from aiogram import Bot, Dispatcher
from aiogram.types import CallbackQuery, Chat, Message, TelegramObject, Update, User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import Booking, Car
from bot.handlers import ai_search, booking, catalog, common


async def test_book_callback_reaches_real_db_through_dispatcher(db_session: AsyncSession) -> None:
    """Feeds a real Update through a real Dispatcher (routers + middleware), the
    same wiring bot/main.py assembles, instead of calling handle_book_callback
    directly. This is the layer where the missing catalog keyboard (Fix 2) lived
    and went unnoticed by every task-scoped test."""

    car = Car(
        make="BMW", model="X5", year=2019, mileage_km=45000, color="black",
        is_new=False, owners_count=2, condition="good", price_eur=28000,
        description="BMW X5", status="available",
    )
    db_session.add(car)
    await db_session.commit()

    dispatcher = Dispatcher()
    dispatcher.include_router(common.router)
    dispatcher.include_router(catalog.router)
    dispatcher.include_router(booking.router)
    dispatcher.include_router(ai_search.router)

    async def inject_session(
        handler: Any, event: TelegramObject, data: dict[str, Any]
    ) -> Any:
        data["session"] = db_session
        return await handler(event, data)

    dispatcher.update.outer_middleware(inject_session)

    bot = Bot(token="123456:TEST-TOKEN-TEST-TOKEN-TEST-TOKE")
    # Never let a real Telegram API call happen; CallbackQuery.answer() is the
    # only outbound call the booking handler makes.
    bot.session.make_request = AsyncMock(return_value=True)  # type: ignore[method-assign]

    chat = Chat(id=1001, type="private")
    user = User(id=42, is_bot=False, first_name="Alice")
    message = Message(
        message_id=1,
        date=datetime.now(UTC),
        chat=chat,
        from_user=user,
        text="привет",
    )
    callback_query = CallbackQuery(
        id="callback-1",
        from_user=user,
        chat_instance="chat-instance-1",
        message=message,
        data=f"book:{car.id}",
    )
    update = Update(update_id=1, callback_query=callback_query)

    await dispatcher.feed_update(bot, update)

    bot.session.make_request.assert_awaited()

    await db_session.refresh(car)
    assert car.status == "reserved"

    result = await db_session.execute(select(Booking).where(Booking.car_id == car.id))
    stored_booking = result.scalar_one()
    assert stored_booking.telegram_user_id == 42
    assert stored_booking.contact_name == "Alice"
