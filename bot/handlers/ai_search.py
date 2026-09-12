import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import Car
from bot.db.repository import search_cars_by_embedding
from bot.i18n import Lang, detect_language, t
from bot.llm.client import ChatClient
from bot.llm.embeddings import EmbeddingClient

router = Router(name="ai_search")
logger = logging.getLogger(__name__)


def _build_prompt(query: str, lang: Lang, cars: list[Car]) -> list[dict[str, str]]:
    listings = "\n".join(
        f"- {c.make} {c.model} {c.year}, {c.mileage_km} km, {c.condition}, EUR {c.price_eur}"
        for c in cars
    )
    language_name = "Russian" if lang == "ru" else "English"
    system = (
        f"You are a car sales assistant. Reply in {language_name}. "
        f"Recommend only from this list:\n{listings}"
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": query},
    ]


async def handle_ai_search_query(
    message: Message,
    session: AsyncSession,
    embedder: EmbeddingClient,
    chat_client: ChatClient,
    top_k: int,
) -> None:
    query = message.text or ""
    lang = detect_language(query)

    try:
        query_embedding = await embedder.embed(query)
        cars = await search_cars_by_embedding(session, query_embedding, top_k)
        if not cars:
            await message.answer(t("no_results", lang))
            return
        reply = await chat_client.chat(_build_prompt(query, lang, cars))
    except Exception:
        # Ollama being unreachable (tunnel/home machine down) must degrade to a
        # friendly message, not a crashed handler — this is the one place we
        # deliberately catch broad exceptions per the spec's error-handling rule.
        logger.exception("ai_search failed")
        await message.answer(t("assistant_unavailable", lang))
        return

    await message.answer(reply)


@router.message(Command("ai_search"))
async def handle_ai_search(
    message: Message,
    session: AsyncSession,
    embedder: EmbeddingClient,
    chat_client: ChatClient,
    ai_search_top_k: int,
) -> None:
    await handle_ai_search_query(message, session, embedder, chat_client, ai_search_top_k)
