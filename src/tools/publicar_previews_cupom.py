import argparse
import asyncio
from datetime import date, datetime
from pathlib import Path

from src.config.settings import get_settings
from src.dto.produto_candidato_dto import ProdutoCandidatoDTO
from src.dto.telegram_message_dto import TelegramMessageDTO
from src.external.cupom.thiago_rodrigo_client import ThiagoRodrigoCupomClient
from src.external.telegram.telegram_client import TelegramClient
from src.service.cupom_postagem_historico_service import CupomPostagemHistoricoService
from src.service.cupom_postagem_service import CupomPostagemService
from src.service.cupom_preview_runner_service import CupomPreviewRunnerService
from src.service.cupom_scraper_service import CupomScraperService


def main() -> None:
    asyncio.run(_main())


async def _main() -> None:
    args = _parse_args()
    data_referencia = _parse_date(args.data_referencia) if args.data_referencia else None
    momento = datetime.now()
    historico_service = CupomPostagemHistoricoService()
    postagens_por_produto = historico_service.carregar_de_arquivo(args.historico)
    runner = CupomPreviewRunnerService(
        scraper_service=CupomScraperService(ThiagoRodrigoCupomClient()),
    )
    resultado = await runner.gerar_previews(
        caminho_produtos=args.produtos,
        data_referencia=data_referencia,
        postagens_por_produto=postagens_por_produto,
        agora=momento,
        limite=args.limite,
        filtrar_cupons=not args.sem_filtro,
    )
    mensagens = [mensagem for _, mensagem in resultado.previews]

    _imprimir_previews(resultado.total_cupons, resultado.total_produtos, mensagens)
    if not args.confirmar_envio:
        print()
        print("Dry-run concluido. Use --confirmar-envio para postar no Telegram.")
        return

    if not mensagens:
        print()
        print("Nenhum preview gerado para publicar.")
        return

    settings = get_settings()
    postagem_service = CupomPostagemService(
        TelegramClient(
            bot_token=settings.telegram_bot_token,
            chat_id=settings.telegram_chat_id,
        )
    )
    resultados = []
    historico_atualizado = postagens_por_produto
    for match, mensagem in resultado.previews:
        resultado_postagem = await postagem_service.publicar(mensagem)
        resultados.append(resultado_postagem)
        historico_atualizado = historico_service.registrar_postagem(
            historico_atualizado,
            _chave_produto(match.produto),
            momento,
        )
        historico_service.salvar_em_arquivo(args.historico, historico_atualizado)

    print()
    print(f"Posts enviados: {len(resultados)}")
    for index, resultado_postagem in enumerate(resultados, start=1):
        print(f"{index}. Telegram message id: {resultado_postagem.telegram_message_id}")


def _imprimir_previews(
    total_cupons: int,
    total_produtos: int,
    mensagens: list[TelegramMessageDTO],
) -> None:
    print(f"Cupons encontrados: {total_cupons}")
    print(f"Produtos candidatos: {total_produtos}")
    print(f"Previews gerados: {len(mensagens)}")

    for index, mensagem in enumerate(mensagens, start=1):
        print()
        print(f"--- Preview {index} ---")
        print(f"Imagem: {mensagem.image_url}")
        print()
        print(mensagem.caption)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gera previews de cupom e publica no Telegram apenas com confirmacao.",
    )
    parser.add_argument(
        "--produtos",
        type=Path,
        default=Path("data/produtos_candidatos.json"),
        help="Caminho do JSON com produtos candidatos.",
    )
    parser.add_argument(
        "--historico",
        type=Path,
        default=Path("data/cupom_postagens.json"),
        help="Caminho do JSON local com historico de posts de cupom.",
    )
    parser.add_argument(
        "--limite",
        type=int,
        default=3,
        help="Quantidade maxima de posts enviados.",
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
    parser.add_argument(
        "--confirmar-envio",
        action="store_true",
        help="Publica os previews gerados no canal configurado em TELEGRAM_CHAT_ID.",
    )
    return parser.parse_args()


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Data precisa estar no formato YYYY-MM-DD.") from exc


def _chave_produto(produto: ProdutoCandidatoDTO) -> str:
    return f"{produto.loja}:{produto.external_id}"


if __name__ == "__main__":
    main()
