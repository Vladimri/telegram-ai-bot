from unittest.mock import AsyncMock

from bot.db.models import Car
from bot.handlers.ai_search import handle_ai_search_query


class _FakeMessage:
    def __init__(self, text: str) -> None:
        self.text = text
        self.answer = AsyncMock()


async def test_handle_ai_search_query_returns_llm_reply(db_session):
    db_session.add(
        Car(
            make="BMW", model="X5", year=2019, mileage_km=45000, color="black",
            is_new=False, owners_count=2, condition="good", price_eur=28000,
            description="BMW X5", embedding=[0.5] * 768, status="available",
        )
    )
    await db_session.commit()

    embedder = AsyncMock()
    embedder.embed.return_value = [0.5] * 768
    chat_client = AsyncMock()
    chat_client.chat.return_value = "I recommend the BMW X5."
    message = _FakeMessage("хочу семейный автомобиль")

    await handle_ai_search_query(message, db_session, embedder, chat_client, top_k=3)

    message.answer.assert_awaited_once_with("I recommend the BMW X5.")


async def test_handle_ai_search_query_reports_unavailable_on_llm_error(db_session):
    embedder = AsyncMock()
    embedder.embed.side_effect = ConnectionError("tunnel down")
    chat_client = AsyncMock()
    message = _FakeMessage("I want a family car")

    await handle_ai_search_query(message, db_session, embedder, chat_client, top_k=3)

    message.answer.assert_awaited_once_with(
        "The AI assistant is temporarily unavailable, please try again later."
    )
