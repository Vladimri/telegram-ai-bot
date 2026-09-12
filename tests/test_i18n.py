from bot.i18n import detect_language, t


def test_detect_language_russian():
    assert detect_language("Привет, хочу купить машину") == "ru"


def test_detect_language_english():
    assert detect_language("Hi, I want to buy a car") == "en"


def test_t_returns_localized_string():
    assert t("no_results", "en") == "No cars match these filters. Try loosening them."
