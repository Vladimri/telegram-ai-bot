from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Car(Base):
    __tablename__ = "cars"
    __table_args__ = (
        CheckConstraint(
            "condition IN ('new', 'excellent', 'good', 'average', 'poor')",
            name="cars_condition_check",
        ),
        CheckConstraint("status IN ('available', 'reserved')", name="cars_status_check"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    make: Mapped[str]
    model: Mapped[str]
    year: Mapped[int]
    mileage_km: Mapped[int]
    color: Mapped[str]
    is_new: Mapped[bool]
    owners_count: Mapped[int]
    condition: Mapped[str]
    price_eur: Mapped[float] = mapped_column(Numeric(10, 2))
    description: Mapped[str]
    embedding: Mapped[list[float] | None] = mapped_column(Vector(768), nullable=True)
    status: Mapped[str] = mapped_column(server_default="available")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'confirmed', 'cancelled')", name="bookings_status_check"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    car_id: Mapped[int] = mapped_column(ForeignKey("cars.id"))
    telegram_user_id: Mapped[int] = mapped_column(BigInteger)
    contact_name: Mapped[str | None]
    status: Mapped[str] = mapped_column(server_default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant')", name="chat_messages_role_check"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_chat_id: Mapped[int] = mapped_column(BigInteger)
    role: Mapped[str]
    content: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
