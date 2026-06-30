import argparse
import asyncio
from datetime import date
from pathlib import Path

from src.external.cupom.thiago_rodrigo_client import ThiagoRodrigoCupomClient
from src.service.cupom_preview_runner_service import CupomPreviewRunnerService
from src.service.cupom_scraper_service import CupomScraperService


def main() -> None:
    asyncio.run(_main())


async def _main() -> None:
    args = _parse_args()
    data_referencia = _parse_date(args.data_referencia) if args.data_referencia else None
    service = CupomPreviewRunnerService(
        scraper_service=CupomScraperService(ThiagoRodrigoCupomClient()),
    )
    resultado = await service.gerar_previews(
        caminho_produtos=args.produtos,
        data_referencia=data_referencia,
        limite=args.limite,
        filtrar_cupons=not args.sem_filtro,
    )

    print(f"Cupons encontrados: {resultado.total_cupons}")
    print(f"Produtos candidatos: {resultado.total_produtos}")
    print(f"Previews gerados: {resultado.total_previews}")

    for index, (match, mensagem) in enumerate(resultado.previews, start=1):
        print()
        print(f"--- Preview {index} ---")
        print(f"Loja: {match.cupom.loja}")
        print(f"Produto: {match.produto.external_id}")
        print(f"Score: {match.score}")
        print(f"Motivo: {match.motivo}")
        print(f"Imagem: {mensagem.image_url}")
        print()
        print(mensagem.caption)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gera previews de posts de cupom sem publicar no Telegram.",
    )
    parser.add_argument(
        "--produtos",
        type=Path,
        default=Path("data/produtos_candidatos.json"),
        help="Caminho do JSON com produtos candidatos.",
    )
    parser.add_argument(
        "--limite",
        type=int,
        default=10,
        help="Quantidade maxima de previews gerados.",
    )
    parser.add_argument(
        "--data-referencia",
        help="Data dos produtos candidatos no formato YYYY-MM-DD. Padrao: hoje.",
    )
    parser.add_argument(
        "--sem-filtro",
        action="store_true",
        help="Mantem todos os cupons extraidos, sem filtrar pelo nicho.",
    )
    return parser.parse_args()


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Data precisa estar no formato YYYY-MM-DD.") from exc


if __name__ == "__main__":
    main()
