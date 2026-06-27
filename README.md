# Sociedade Do Cupom Bot

Bot Python para buscar ofertas de afiliados, filtrar produtos do nicho de tecnologia e publicar no canal do Telegram Sociedade Do Cupom.

## Stack

- Python 3.12+
- uv
- PostgreSQL/Supabase
- SQLAlchemy 2 async + asyncpg
- Alembic
- httpx
- APScheduler
- pytest + Ruff + mypy

## Como rodar localmente

1. Copie `.env.example` para `.env` e preencha as variaveis.
2. Instale as dependencias:

```bash
uv sync
```

3. Rode as migrations:

```bash
uv run alembic upgrade head
```

4. Inicie o bot:

```bash
uv run python -m src.main
```

## Testes

```bash
uv run pytest --cov=src --cov-report=term-missing
uv run ruff format --check .
uv run ruff check .
uv run mypy src
```
