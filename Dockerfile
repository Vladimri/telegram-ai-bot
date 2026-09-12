FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml ./
COPY bot ./bot
COPY scripts ./scripts
RUN pip install --no-cache-dir .

COPY alembic ./alembic
COPY alembic.ini ./

CMD ["python", "-m", "bot.main"]
