# tests/test_migrations.py
import sqlalchemy as sa


async def test_tables_exist_after_migration(db_session):
    result = await db_session.execute(
        sa.text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    )
    tables = {row[0] for row in result}
    assert {"cars", "bookings", "chat_messages"} <= tables


async def test_vector_extension_installed(db_session):
    result = await db_session.execute(
        sa.text("SELECT extname FROM pg_extension WHERE extname = 'vector'")
    )
    assert result.scalar_one_or_none() == "vector"
