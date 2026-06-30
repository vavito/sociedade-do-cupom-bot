import argparse
import asyncio
from datetime import date
from decimal import Decimal
from pathlib import Path

from src.dto.produto_candidato_dto import ProdutoCandidatoDTO
from src.external.produto.browser_produto_client import BrowserProdutoClient
from src.external.produto.marketplace_produto_client import MarketplaceProdutoClient
from src.service.fonte_produto_seed_service import FonteProdutoSeedService
from src.service.produto_candidato_catalogo_service import ProdutoCandidatoCatalogoService
from src.service.produto_candidato_scraper_service import (
    ProdutoCandidatoScraperService,
    ProdutoHtmlClient,
)


def main() -> None:
    asyncio.run(_main())


async def _main() -> None:
    args = _parse_args()
    data_referencia = _parse_date(args.data_referencia) if args.data_referencia else None
    fonte_service = FonteProdutoSeedService()
    catalogo_service = ProdutoCandidatoCatalogoService()
    scraper_service = ProdutoCandidatoScraperService(
        _criar_client(args),
        catalogo_service=catalogo_service,
    )

    fontes = fonte_service.carregar_de_arquivo(args.fontes)
    encontrados = await scraper_service.buscar_produtos(
        fontes,
        data_referencia=data_referencia,
        limite_por_fonte=args.limite_por_fonte,
    )
    produtos_finais = (
        _combinar_produtos(catalogo_service.listar(args.saida), encontrados, catalogo_service)
        if args.manter_existentes
        else encontrados
    )

    _imprimir_resultado(len(fontes), encontrados, produtos_finais)
    if not args.salvar:
        print()
        print("Dry-run concluido. Use --salvar para atualizar o JSON de produtos candidatos.")
        return

    catalogo_service.salvar(args.saida, produtos_finais)
    print()
    print(f"Arquivo atualizado: {args.saida}")


def _combinar_produtos(
    existentes: list[ProdutoCandidatoDTO],
    encontrados: list[ProdutoCandidatoDTO],
    catalogo_service: ProdutoCandidatoCatalogoService,
) -> list[ProdutoCandidatoDTO]:
    produtos_por_chave = {
        catalogo_service.chave_produto(produto): produto for produto in existentes
    }
    for produto in encontrados:
        produtos_por_chave[catalogo_service.chave_produto(produto)] = produto
    return list(produtos_por_chave.values())


def _criar_client(args: argparse.Namespace) -> ProdutoHtmlClient:
    if args.browser:
        return BrowserProdutoClient(
            user_data_dir=args.browser_perfil,
            headless=not args.browser_visivel,
            timeout_ms=args.browser_timeout,
            scrolls=args.browser_scrolls,
            delay_ms=args.browser_delay,
        )
    return MarketplaceProdutoClient()


def _imprimir_resultado(
    total_fontes: int,
    encontrados: list[ProdutoCandidatoDTO],
    produtos_finais: list[ProdutoCandidatoDTO],
) -> None:
    print(f"Fontes carregadas: {total_fontes}")
    print(f"Produtos encontrados: {len(encontrados)}")
    print(f"Produtos finais: {len(produtos_finais)}")

    for produto in produtos_finais:
        print(
            " | ".join(
                [
                    f"{produto.loja}:{produto.external_id}",
                    produto.categoria or "sem_categoria",
                    f"R$ {_formatar_decimal(produto.preco)}",
                    produto.titulo,
                ]
            )
        )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Atualiza produtos candidatos a partir de fontes de Amazon e Mercado Livre.",
    )
    parser.add_argument(
        "--fontes",
        type=Path,
        default=Path("data/fontes_produtos.json"),
        help="Caminho do JSON com fontes de produtos.",
    )
    parser.add_argument(
        "--saida",
        type=Path,
        default=Path("data/produtos_candidatos.json"),
        help="Caminho do JSON de produtos candidatos.",
    )
    parser.add_argument(
        "--limite-por-fonte",
        type=int,
        default=10,
        help="Quantidade maxima de produtos aceitos por fonte.",
    )
    parser.add_argument(
        "--data-referencia",
        help="Data dos produtos candidatos no formato YYYY-MM-DD. Padrao: vazio.",
    )
    parser.add_argument(
        "--manter-existentes",
        action="store_true",
        help="Mantem produtos ja cadastrados e substitui apenas duplicados encontrados.",
    )
    parser.add_argument(
        "--salvar",
        action="store_true",
        help="Atualiza o arquivo de saida. Sem essa flag, roda em dry-run.",
    )
    parser.add_argument(
        "--browser",
        action="store_true",
        help="Busca as fontes usando Playwright/Chromium em vez de HTTP direto.",
    )
    parser.add_argument(
        "--browser-visivel",
        action="store_true",
        help="Abre o navegador visivel. Util para primeiro login/cookies e debug.",
    )
    parser.add_argument(
        "--browser-perfil",
        type=Path,
        default=Path(".browser/produtos"),
        help="Diretorio local do perfil persistente do Chromium.",
    )
    parser.add_argument(
        "--browser-timeout",
        type=int,
        default=45_000,
        help="Timeout de navegacao do browser em milissegundos.",
    )
    parser.add_argument(
        "--browser-scrolls",
        type=int,
        default=3,
        help="Quantidade de rolagens antes de capturar o HTML renderizado.",
    )
    parser.add_argument(
        "--browser-delay",
        type=int,
        default=800,
        help="Espera em milissegundos entre rolagens do browser.",
    )
    return parser.parse_args()


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Data precisa estar no formato YYYY-MM-DD.") from exc


def _formatar_decimal(valor: Decimal) -> str:
    texto = f"{valor:.0f}" if valor == valor.to_integral() else f"{valor:.2f}"
    return texto.replace(".", ",")


if __name__ == "__main__":
    main()
