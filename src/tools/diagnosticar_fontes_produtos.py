import argparse
import asyncio
from datetime import date
from decimal import Decimal
from pathlib import Path

from src.dto.produto_fonte_diagnostico_dto import ProdutoFonteDiagnosticoDTO
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
    fontes = FonteProdutoSeedService().carregar_de_arquivo(args.fontes)
    scraper_service = ProdutoCandidatoScraperService(
        _criar_client(args),
        catalogo_service=ProdutoCandidatoCatalogoService(),
    )

    diagnosticos = await scraper_service.diagnosticar_fontes(
        fontes=fontes,
        data_referencia=data_referencia,
        limite_por_fonte=args.limite_por_fonte,
    )

    _imprimir_diagnosticos(diagnosticos)


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


def _imprimir_diagnosticos(diagnosticos: list[ProdutoFonteDiagnosticoDTO]) -> None:
    total_produtos = sum(diagnostico.total_aceitos for diagnostico in diagnosticos)
    total_blocos = sum(diagnostico.total_blocos for diagnostico in diagnosticos)
    print(f"Fontes diagnosticadas: {len(diagnosticos)}")
    print(f"Cards parseaveis: {total_blocos}")
    print(f"Produtos aceitos: {total_produtos}")

    for diagnostico in diagnosticos:
        print()
        print(f"--- {diagnostico.fonte.loja}/{diagnostico.fonte.categoria} ---")
        print(f"URL: {diagnostico.fonte.url}")
        print(f"Cards parseaveis: {diagnostico.total_blocos}")
        print(f"Produtos aceitos: {diagnostico.total_aceitos}")

        if diagnostico.erro:
            print(f"Erro: {diagnostico.erro}")
        elif diagnostico.motivo_sem_produtos and diagnostico.total_aceitos == 0:
            print(f"Motivo: {diagnostico.motivo_sem_produtos}")

        if diagnostico.rejeicoes:
            rejeicoes = ", ".join(
                f"{motivo}={quantidade}"
                for motivo, quantidade in sorted(diagnostico.rejeicoes.items())
            )
            print(f"Rejeicoes: {rejeicoes}")

        for produto in diagnostico.produtos:
            marca = produto.marca or "sem_marca"
            print(
                " | ".join(
                    [
                        f"R$ {_formatar_decimal(produto.preco)}",
                        marca,
                        produto.titulo,
                    ]
                )
            )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Diagnostica fontes de produtos por loja, categoria e motivo de rejeicao.",
    )
    parser.add_argument(
        "--fontes",
        type=Path,
        default=Path("data/fontes_produtos.json"),
        help="Caminho do JSON com fontes de produtos.",
    )
    parser.add_argument(
        "--limite-por-fonte",
        type=int,
        default=3,
        help="Quantidade maxima de produtos aceitos por fonte no diagnostico.",
    )
    parser.add_argument(
        "--data-referencia",
        help="Data dos produtos candidatos no formato YYYY-MM-DD. Padrao: vazio.",
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
