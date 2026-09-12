from bot.db.repository import CarFilters, list_cars
from scripts.seed_cars import seed_cars


class _StubEmbedder:
    async def embed(self, text: str) -> list[float]:
        return [0.0] * 768


async def test_seed_cars_inserts_requested_count(db_session):
    cars = await seed_cars(db_session, _StubEmbedder(), count=5)

    assert len(cars) == 5
    assert all(car.embedding is not None for car in cars)

    stored = await list_cars(db_session, CarFilters(), limit=10)
    assert len(stored) == 5
