import os
import subprocess
import sys
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL", "postgresql+asyncpg://bot:bot@localhost:55432/telegram_ai_bot_test"
)


def _migration_env() -> dict[str, str]:
    return {
        **os.environ,
        "DATABASE_URL": TEST_DATABASE_URL,
        "BOT_TOKEN": os.environ.get("BOT_TOKEN", "test-token"),
        "OLLAMA_BASE_URL": os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
    }


@pytest.fixture(scope="session", autouse=True)
def apply_migrations() -> None:
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        check=True,
        env=_migration_env(),
    )


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(TEST_DATABASE_URL)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        yield session
        await session.rollback()

    async with engine.begin() as conn:
        for table in ("bookings", "chat_messages", "cars"):
            await conn.execute(sa.text(f"TRUNCATE {table} RESTART IDENTITY CASCADE"))

    await engine.dispose()
