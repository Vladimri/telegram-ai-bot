import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.types import ErrorEvent, TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from bot.config import Settings
from bot.handlers import ai_search, booking, catalog, common
from bot.llm.client import ChatClient
from bot.llm.embeddings import EmbeddingClient


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    settings = Settings()

    engine = create_async_engine(settings.database_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    embedder = EmbeddingClient(settings.ollama_base_url, settings.ollama_embed_model)
    chat_client = ChatClient(settings.ollama_base_url, settings.ollama_chat_model)

    bot = Bot(token=settings.bot_token)
    dispatcher = Dispatcher()
    dispatcher.include_router(common.router)
    dispatcher.include_router(catalog.router)
    dispatcher.include_router(booking.router)
    dispatcher.include_router(ai_search.router)

    dispatcher["embedder"] = embedder
    dispatcher["chat_client"] = chat_client
    dispatcher["ai_search_top_k"] = settings.ai_search_top_k

    async def inject_session(
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        async with session_factory() as session:
            data["session"] = session
            return await handler(event, data)

    dispatcher.update.outer_middleware(inject_session)

    @dispatcher.errors()
    async def handle_errors(event: ErrorEvent) -> None:
        logging.getLogger(__name__).exception("Unhandled error", exc_info=event.exception)

    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
