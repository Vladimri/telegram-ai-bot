from dataclasses import dataclass

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import Booking, Car


@dataclass
class CarFilters:
    make: str | None = None
    max_price_eur: float | None = None
    min_year: int | None = None
    condition: str | None = None


async def list_cars(session: AsyncSession, filters: CarFilters, limit: int = 10) -> list[Car]:
    query = select(Car).where(Car.status == "available")
    if filters.make:
        query = query.where(Car.make.ilike(filters.make))
    if filters.max_price_eur is not None:
        query = query.where(Car.price_eur <= filters.max_price_eur)
    if filters.min_year is not None:
        query = query.where(Car.year >= filters.min_year)
    if filters.condition:
        query = query.where(Car.condition == filters.condition)
    query = query.order_by(Car.created_at.desc()).limit(limit)

    result = await session.execute(query)
    return list(result.scalars().all())


async def book_car(
    session: AsyncSession, car_id: int, telegram_user_id: int, contact_name: str | None
) -> Booking | None:
    result = await session.execute(
        update(Car)
        .where(Car.id == car_id, Car.status == "available")
        .values(status="reserved")
        .returning(Car.id)
    )
    if result.first() is None:
        return None

    booking = Booking(car_id=car_id, telegram_user_id=telegram_user_id, contact_name=contact_name)
    session.add(booking)
    await session.commit()
    return booking


async def search_cars_by_embedding(
    session: AsyncSession, embedding: list[float], top_k: int
) -> list[Car]:
    query = (
        select(Car)
        .where(Car.status == "available")
        .order_by(Car.embedding.cosine_distance(embedding))
        .limit(top_k)
    )
    result = await session.execute(query)
    return list(result.scalars().all())
