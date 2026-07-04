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

## Cupons e produtos candidatos

O modulo `cupom` extrai cupons da Amazon e do Mercado Livre no Thiago Rodrigo e permite cruzar esses cupons com produtos candidatos do dia.

Nesta fase, os produtos candidatos podem ser carregados manualmente por JSON, usando o exemplo:

```txt
data/produtos_candidatos.example.json
```

Crie o arquivo local de trabalho copiando o exemplo:

```bash
cp data/produtos_candidatos.example.json data/produtos_candidatos.json
```

Esse arquivo real fica ignorado no Git, entao pode receber links, precos e produtos do dia.

As fontes de scraping ficam em outro JSON local. Copie o exemplo com URLs de Amazon e Mercado Livre:

```bash
cp data/fontes_produtos.example.json data/fontes_produtos.json
```

O arquivo `data/fontes_produtos.example.json` versiona as URLs base de cada categoria do nicho. O bot usa o arquivo local `data/fontes_produtos.json`, que fica ignorado no Git para voce ajustar URLs e filtros sem afetar o repositorio.

Para buscar produtos candidatos dessas fontes sem salvar:

```bash
uv run python -m src.tools.atualizar_produtos_candidatos --limite-por-fonte 5
```

Para diagnosticar cada fonte antes de salvar produtos, mostrando quantos cards foram encontrados, quantos produtos passaram nos filtros e os principais motivos de rejeicao:

```bash
uv run python -m src.tools.diagnosticar_fontes_produtos --browser --limite-por-fonte 3
```

Para diagnosticar apenas algumas categorias ou lojas:

```bash
uv run python -m src.tools.diagnosticar_fontes_produtos --browser --limite-por-fonte 3 --categoria headset_fone --categoria teclado --categoria acessorio
uv run python -m src.tools.diagnosticar_fontes_produtos --browser --loja amazon --categoria headset_fone
```

Se HTTP direto retornar bloqueio ou HTML incompleto, instale o Chromium do Playwright:

```bash
uv run playwright install chromium
```

E rode a coleta com navegador real:

```bash
uv run python -m src.tools.atualizar_produtos_candidatos --browser --limite-por-fonte 5
```

Para abrir o navegador visivel e reaproveitar cookies/sessao no perfil local `.browser/produtos`:

```bash
uv run python -m src.tools.atualizar_produtos_candidatos --browser --browser-visivel --limite-por-fonte 5
```

Para atualizar `data/produtos_candidatos.json` com o resultado do scraping:

```bash
uv run python -m src.tools.atualizar_produtos_candidatos --limite-por-fonte 5 --salvar
```

Use `--manter-existentes` quando quiser preservar produtos cadastrados manualmente e substituir apenas duplicados encontrados pelo scraper.

Em `data/fontes_produtos.json`, fontes de categorias sensiveis como headset e teclado podem usar:

```json
"marcas_prioritarias": ["havit", "jbl", "redragon", "logitech"],
"exigir_marca_prioritaria": true,
"limite_por_marca": 2
```

Isso evita produtos genericos demais e limita repeticao de uma mesma marca dentro da categoria.

Voce tambem pode gerenciar esse JSON por comando:

```bash
uv run python -m src.tools.produtos_candidatos listar
```

Para adicionar um produto candidato:

```bash
uv run python -m src.tools.produtos_candidatos adicionar --loja amazon --external-id amazon-monitor-lg-24 --titulo "Monitor gamer LG 24 polegadas 144Hz" --url "https://www.amazon.com.br/produto" --preco 999.90 --marca LG
```

Para remover:

```bash
uv run python -m src.tools.produtos_candidatos remover --loja amazon --external-id amazon-monitor-lg-24
```

O fluxo gera previews de posts e so publica quando o comando de envio recebe confirmacao explicita:

```txt
cupons do dia + produtos candidatos do dia -> match por loja/nicho/preco -> preview de post
```

Para testar a geracao dos posts sem enviar nada ao Telegram:

```bash
uv run python -m src.tools.gerar_previews_cupom --limite 5
```

Para testar uma data especifica:

```bash
uv run python -m src.tools.gerar_previews_cupom --data-referencia 2026-06-30
```

Para simular o fluxo de publicacao sem enviar nada:

```bash
uv run python -m src.tools.publicar_previews_cupom --limite 3
```

Esse comando considera o historico local de posts em `data/cupom_postagens.json`, criado automaticamente apos envios confirmados. O arquivo fica ignorado no Git.

Para publicar os previews gerados no canal configurado em `TELEGRAM_CHAT_ID`:

```bash
uv run python -m src.tools.publicar_previews_cupom --limite 3 --confirmar-envio
```

Para rodar a rotina diaria completa, atualizando produtos candidatos, buscando cupons, gerando previews e mantendo o envio em dry-run:

```bash
uv run python -m src.tools.rotina_cupons --browser --limite-por-fonte 5 --limite 3
```

Esse comando salva `data/produtos_candidatos.json` por padrao antes de montar os previews, para usar os produtos recem-coletados. Se quiser apenas simular sem atualizar o JSON de produtos:

```bash
uv run python -m src.tools.rotina_cupons --browser --nao-salvar-produtos
```

Para enviar os posts gerados no canal, a rotina tambem exige confirmacao explicita:

```bash
uv run python -m src.tools.rotina_cupons --browser --limite 3 --confirmar-envio
```

Para testar com um historico separado:

```bash
uv run python -m src.tools.publicar_previews_cupom --historico data/cupom_postagens.teste.json
```

O repost do mesmo produto respeita intervalo minimo de 6h no mesmo dia e bloqueia reposts apos 18h quando o produto ja saiu naquele dia.

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
