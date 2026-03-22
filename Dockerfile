FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project --no-dev

COPY ./bot.py bot.py
COPY ./voicetools voicetools

EXPOSE 7860

CMD ["uv", "run", "bot.py"]
