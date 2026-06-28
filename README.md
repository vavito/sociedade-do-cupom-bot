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

## Supabase

Use a connection string do Supabase com o driver async do projeto:

```env
DATABASE_URL=postgresql+asyncpg://postgres.PROJECT_REF:SENHA@HOST:5432/postgres?ssl=require
```

Para desenvolvimento local, prefira a URL do **Session Pooler** no painel do Supabase. Ela costuma funcionar melhor em redes IPv4 e evita problemas de prepared statements comuns no Transaction Pooler.

Depois de preencher o `.env`, aplique o schema:

```bash
uv run alembic upgrade head
```

Se voce so tiver a URL do **Transaction Pooler** na porta `6543`, adicione `prepared_statement_cache_size=0` na query string:

```env
DATABASE_URL=postgresql+asyncpg://postgres.PROJECT_REF:SENHA@HOST:6543/postgres?ssl=require&prepared_statement_cache_size=0
```

## Testes

```bash
uv run pytest --cov=src --cov-report=term-missing
uv run ruff format --check .
uv run ruff check .
uv run mypy src
```
