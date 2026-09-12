from bot.db.models import Car
from bot.db.repository import CarFilters, book_car, list_cars, search_cars_by_embedding


def _make_car(**overrides):
    defaults = dict(
        make="BMW", model="X5", year=2019, mileage_km=45000, color="black",
        is_new=False, owners_count=2, condition="good", price_eur=28000,
        description="BMW X5 2019", status="available",
    )
    defaults.update(overrides)
    return Car(**defaults)


async def test_list_cars_filters_by_make(db_session):
    db_session.add_all([_make_car(make="BMW"), _make_car(make="Audi", model="A4")])
    await db_session.commit()

    result = await list_cars(db_session, CarFilters(make="BMW"))

    assert len(result) == 1
    assert result[0].make == "BMW"


async def test_book_car_marks_reserved(db_session):
    car = _make_car()
    db_session.add(car)
    await db_session.commit()

    booking = await book_car(db_session, car.id, telegram_user_id=123, contact_name="Alice")

    assert booking is not None
    assert booking.car_id == car.id
    await db_session.refresh(car)
    assert car.status == "reserved"


async def test_book_car_returns_none_if_already_reserved(db_session):
    car = _make_car(status="reserved")
    db_session.add(car)
    await db_session.commit()

    booking = await book_car(db_session, car.id, telegram_user_id=123, contact_name="Alice")

    assert booking is None


async def test_search_cars_by_embedding_orders_by_similarity(db_session):
    close = _make_car(make="BMW", embedding=[1.0] * 768)
    far = _make_car(make="Audi", model="A4", embedding=[-1.0] * 768)
    db_session.add_all([close, far])
    await db_session.commit()

    result = await search_cars_by_embedding(db_session, embedding=[1.0] * 768, top_k=2)

    assert result[0].make == "BMW"
