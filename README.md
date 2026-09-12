# telegram-ai-bot

Telegram bot for browsing a car catalog, requesting bookings, and getting
AI-assisted recommendations (RAG over Postgres/pgvector).

## Local development

1. Copy `.env.example` to `.env` and fill in `BOT_TOKEN` and `OLLAMA_BASE_URL`.
2. `docker compose up --build`
3. Apply migrations: `docker compose exec bot alembic upgrade head`
4. Seed test data: `docker compose exec bot python -m scripts.seed_cars`

## Tests

1. `docker compose -f docker-compose.test.yml up -d`
2. `pip install -e ".[dev]"`
3. `pytest`
