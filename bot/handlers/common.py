from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.i18n import detect_language, t

router = Router(name="common")


@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    lang = detect_language(message.text or "")
    await message.answer(t("welcome", lang))
