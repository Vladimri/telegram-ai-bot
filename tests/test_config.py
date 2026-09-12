import pytest
from pydantic import ValidationError

from bot.config import Settings


def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("BOT_TOKEN", "test-token")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost/db")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434")

    settings = Settings(_env_file=None)

    assert settings.bot_token == "test-token"
    assert settings.ollama_chat_model == "llama3.1:8b"
    assert settings.ai_search_top_k == 5


def test_settings_requires_bot_token(monkeypatch):
    monkeypatch.delenv("BOT_TOKEN", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost/db")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434")

    with pytest.raises(ValidationError):
        Settings(_env_file=None)
