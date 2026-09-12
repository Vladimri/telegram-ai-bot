from unittest.mock import AsyncMock

from bot.db.models import Car
from bot.db.repository import CarFilters
from bot.handlers.catalog import show_catalog


class _FakeMessage:
    def __init__(self, text: str) -> None:
        self.text = text
        self.answer = AsyncMock()


async def test_show_catalog_lists_available_cars(db_session):
    db_session.add(
        Car(
            make="BMW", model="X5", year=2019, mileage_km=45000, color="black",
            is_new=False, owners_count=2, condition="good", price_eur=28000,
            description="BMW X5", status="available",
        )
    )
    await db_session.commit()
    message = _FakeMessage("/catalog")

    await show_catalog(message, db_session, CarFilters())

    message.answer.assert_awaited_once()
    assert "BMW X5" in message.answer.call_args.args[0]


async def test_show_catalog_reports_no_results(db_session):
    message = _FakeMessage("/catalog")

    await show_catalog(message, db_session, CarFilters(make="Ferrari"))

    message.answer.assert_awaited_once_with(
        "No cars match these filters. Try loosening them."
    )
