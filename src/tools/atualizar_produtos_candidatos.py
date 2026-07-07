import argparse
import asyncio
from datetime import date
from decimal import Decimal
from pathlib import Path

from src.external.produto.browser_produto_client import BrowserProdutoClient
from src.external.produto.marketplace_produto_client import MarketplaceProdutoClient
from src.service.fonte_produto_seed_service import FonteProdutoSeedService
from src.service.produto_candidato_catalogo_service import ProdutoCandidatoCatalogoService
from src.service.produto_candidato_scraper_service import (
    ProdutoCandidatoScraperService,
    ProdutoHtmlClient,
)
from src.service.produto_candidato_update_service import (
    ProdutoCandidatoUpdateResultado,
    ProdutoCandidatoUpdateService,
)
from src.tools.filtros_fontes_produto import (
    adicionar_argumentos_filtro_fontes,
    filtrar_fontes,
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
    update_service = ProdutoCandidatoUpdateService(
        scraper_service=scraper_service,
        fonte_service=fonte_service,
        catalogo_service=catalogo_service,
    )
    fontes = filtrar_fontes(
        fonte_service.carregar_de_arquivo(args.fontes),
        lojas=args.lojas,
        categorias=args.categorias,
    )

    resultado = await update_service.atualizar_por_fontes(
        fontes=fontes,
        caminho_saida=args.saida,
        data_referencia=data_referencia,
        limite_por_fonte=args.limite_por_fonte,
        manter_existentes=args.manter_existentes,
        salvar=args.salvar,
    )

    _imprimir_resultado(resultado)
    if not args.salvar:
        print()
        print("Dry-run concluido. Use --salvar para atualizar o JSON de produtos candidatos.")
        return

    print()
    print(f"Arquivo atualizado: {args.saida}")


def _criar_client(args: argparse.Namespace) -> ProdutoHtmlClient:
    if args.browser:
        return BrowserProdutoClient(
            user_data_dir=args.browser_perfil,
            headless=not args.browser_visivel,
            timeout_ms=args.browser_timeout,
            scrolls=args.browser_scrolls,
            delay_ms=args.browser_delay,
            security_wait_ms=args.browser_espera_seguranca,
        )
    return MarketplaceProdutoClient()


def _imprimir_resultado(resultado: ProdutoCandidatoUpdateResultado) -> None:
    print(f"Fontes carregadas: {resultado.total_fontes}")
    print(f"Produtos encontrados: {len(resultado.encontrados)}")
    print(f"Produtos finais: {len(resultado.produtos_finais)}")

    for produto in resultado.produtos_finais:
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
    adicionar_argumentos_filtro_fontes(parser)
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
    parser.add_argument(
        "--browser-espera-seguranca",
        type=int,
        default=0,
        help=(
            "Espera em milissegundos para resolver captcha/pagina de seguranca no browser visivel."
        ),
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
