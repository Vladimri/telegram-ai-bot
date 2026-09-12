import asyncio
import random

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from bot.config import Settings
from bot.db.models import Car
from bot.llm.embeddings import EmbeddingClient

MAKES_MODELS = [
    ("BMW", "X5"), ("BMW", "3 Series"), ("Audi", "A4"), ("Audi", "Q5"),
    ("Toyota", "Corolla"), ("Toyota", "RAV4"), ("Volkswagen", "Golf"),
    ("Mercedes-Benz", "C-Class"), ("Ford", "Focus"), ("Hyundai", "Tucson"),
]
COLORS = ["black", "white", "silver", "blue", "red", "grey"]
CONDITIONS = ["excellent", "good", "average", "poor"]


def _build_description(
    make: str, model: str, year: int, mileage_km: int, color: str, condition: str, price_eur: float
) -> str:
    return (
        f"{make} {model}, {year}, {mileage_km} km mileage, {color}, "
        f"condition: {condition}, price: EUR {price_eur:.0f}"
    )


async def seed_cars(session: AsyncSession, embedder: EmbeddingClient, count: int) -> list[Car]:
    cars = []
    for _ in range(count):
        make, model = random.choice(MAKES_MODELS)
        year = random.randint(2005, 2025)
        is_new = year == 2025 and random.random() < 0.2
        mileage_km = 0 if is_new else random.randint(1_000, 220_000)
        color = random.choice(COLORS)
        condition = "new" if is_new else random.choice(CONDITIONS)
        owners_count = 0 if is_new else random.randint(1, 4)
        price_eur = round(random.uniform(4_000, 90_000), 2)
        description = _build_description(make, model, year, mileage_km, color, condition, price_eur)
        embedding = await embedder.embed(description)

        cars.append(
            Car(
                make=make, model=model, year=year, mileage_km=mileage_km, color=color,
                is_new=is_new, owners_count=owners_count, condition=condition,
                price_eur=price_eur, description=description, embedding=embedding,
            )
        )

    session.add_all(cars)
    await session.commit()
    return cars


async def main() -> None:
    settings = Settings()
    engine = create_async_engine(settings.database_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    embedder = EmbeddingClient(settings.ollama_base_url, settings.ollama_embed_model)

    async with session_factory() as session:
        cars = await seed_cars(session, embedder, count=200)
        print(f"Seeded {len(cars)} cars")

    # ivfflat needs existing rows to train its clusters on, so the index is built
    # here, after seeding, rather than in the initial migration against an empty
    # table. Size `lists` off the row count instead of leaving it at a bare default.
    lists = max(int(len(cars) ** 0.5), 1)
    async with engine.begin() as conn:
        await conn.execute(
            sa.text(
                f"CREATE INDEX IF NOT EXISTS cars_embedding_idx ON cars "
                f"USING ivfflat (embedding vector_cosine_ops) WITH (lists = {lists})"
            )
        )

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
