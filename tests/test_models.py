from bot.db.models import Base, Booking, Car, ChatMessage  # noqa: F401


def test_tables_registered_on_metadata():
    assert set(Base.metadata.tables) == {"cars", "bookings", "chat_messages"}


def test_car_table_columns():
    columns = set(Base.metadata.tables["cars"].columns.keys())
    assert columns == {
        "id", "make", "model", "year", "mileage_km", "color", "is_new",
        "owners_count", "condition", "price_eur", "description", "embedding",
        "status", "created_at",
    }
