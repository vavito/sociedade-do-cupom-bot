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

Por padrao, o servico inicia o scheduler automatico e o bot conversacional do Telegram. Para rodar apenas uma parte, ajuste no `.env`:

```env
SCHEDULER_ENABLED=true
TELEGRAM_POST_BOT_ENABLED=true
```

No chat privado com o bot do Telegram, use:

```txt
1. Gerar post
2. Sair
```

Ao escolher gerar post, envie um link de produto da AliExpress. O bot monta o texto do post, oferece postar no canal configurado em `TELEGRAM_CHAT_ID` ou gerar um novo post.

## Shopee

A integracao Shopee usa a API GraphQL de afiliados:

```env
SHOPEE_APP_ID=
SHOPEE_SECRET=
SHOPEE_SUB_ID=telegram
SHOPEE_API_BASE_URL=https://open-api.affiliate.shopee.com.br/graphql
```

O cliente assina cada requisicao com o header `Authorization` no formato exigido pela Shopee e expõe buscas de ofertas de produto, ofertas de loja e geracao de short link.

## Supabase

Use a connection string do Supabase com o driver async do projeto:

```env
DATABASE_URL=postgresql+asyncpg://postgres.PROJECT_REF:SENHA@HOST:5432/postgres?ssl=require
```

Se a senha tiver caracteres especiais, como `@`, `#`, `/`, `?` ou `%`, aplique URL encode antes de colocar na `DATABASE_URL`. Exemplo: `@` vira `%40`.

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
