from typing import Literal

Lang = Literal["ru", "en"]

_CYRILLIC = set("абвгдеёжзийклмнопрстуфхцчшщъыьэюя")


def detect_language(text: str) -> Lang:
    return "ru" if any(ch in _CYRILLIC for ch in text.lower()) else "en"


_STRINGS: dict[str, dict[Lang, str]] = {
    "welcome": {
        "ru": (
            "Привет! Я помогу подобрать автомобиль. "
            "/catalog — каталог, /ai_search — подбор с ИИ."
        ),
        "en": (
            "Hi! I'll help you find a car. "
            "Use /catalog to browse or /ai_search for AI-assisted search."
        ),
    },
    "no_results": {
        "ru": "По этим фильтрам ничего не нашлось. Попробуйте смягчить условия.",
        "en": "No cars match these filters. Try loosening them.",
    },
    "car_reserved": {
        "ru": "Этот автомобиль уже забронирован кем-то другим.",
        "en": "That car was just reserved by someone else.",
    },
    "booking_confirmed": {
        "ru": "Заявка принята! Мы свяжемся с вами.",
        "en": "Booking request received! We'll be in touch.",
    },
    "assistant_unavailable": {
        "ru": "ИИ-ассистент временно недоступен, попробуйте позже.",
        "en": "The AI assistant is temporarily unavailable, please try again later.",
    },
    "book": {
        "ru": "Забронировать",
        "en": "Book",
    },
}


def t(key: str, lang: Lang) -> str:
    return _STRINGS[key][lang]
