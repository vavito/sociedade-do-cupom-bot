import argparse
import asyncio
from datetime import date, datetime
from pathlib import Path

from src.config.settings import get_settings
from src.dto.telegram_message_dto import TelegramMessageDTO
from src.external.cupom.thiago_rodrigo_client import ThiagoRodrigoCupomClient
from src.external.produto.browser_produto_client import BrowserProdutoClient
from src.external.produto.marketplace_produto_client import MarketplaceProdutoClient
from src.external.telegram.telegram_client import TelegramClient
from src.service.cupom_postagem_historico_service import CupomPostagemHistoricoService
from src.service.cupom_postagem_service import CupomPostagemService
from src.service.cupom_preview_runner_service import CupomPreviewRunnerService
from src.service.cupom_rotina_diaria_service import (
    CupomRotinaDiariaResultado,
    CupomRotinaDiariaService,
)
from src.service.cupom_scraper_service import CupomScraperService
from src.service.fonte_produto_seed_service import FonteProdutoSeedService
from src.service.produto_candidato_catalogo_service import ProdutoCandidatoCatalogoService
from src.service.produto_candidato_scraper_service import (
    ProdutoCandidatoScraperService,
    ProdutoHtmlClient,
)
from src.service.produto_candidato_update_service import ProdutoCandidatoUpdateService


def main() -> None:
    asyncio.run(_main())


async def _main() -> None:
    args = _parse_args()
    data_referencia = _parse_date(args.data_referencia) if args.data_referencia else None
    momento = datetime.now()

    service = _criar_rotina_service(args)
    resultado = await service.executar(
        caminho_fontes=args.fontes,
        caminho_produtos=args.produtos,
        caminho_historico=args.historico,
        data_referencia=data_referencia,
        limite_por_fonte=args.limite_por_fonte,
        limite_posts=args.limite,
        manter_existentes=args.manter_existentes,
        salvar_produtos=args.salvar_produtos,
        confirmar_envio=args.confirmar_envio,
        filtrar_cupons=not args.sem_filtro,
        agora=momento,
    )

    _imprimir_resultado(resultado)
    if not args.confirmar_envio:
        print()
        print("Dry-run concluido. Use --confirmar-envio para postar no Telegram.")
        if not args.salvar_produtos:
            print("Produtos nao foram salvos; previews usaram o JSON atual de produtos.")
        return

    print()
    if not resultado.postagens:
        print("Nenhum preview gerado para publicar.")
        return

    print(f"Posts enviados: {len(resultado.postagens)}")
    for index, postagem in enumerate(resultado.postagens, start=1):
        print(f"{index}. Telegram message id: {postagem.telegram_message_id}")


def _criar_rotina_service(args: argparse.Namespace) -> CupomRotinaDiariaService:
    catalogo_service = ProdutoCandidatoCatalogoService()
    produto_scraper_service = ProdutoCandidatoScraperService(
        _criar_produto_client(args),
        catalogo_service=catalogo_service,
    )
    produto_update_service = ProdutoCandidatoUpdateService(
        scraper_service=produto_scraper_service,
        fonte_service=FonteProdutoSeedService(),
        catalogo_service=catalogo_service,
    )
    preview_runner = CupomPreviewRunnerService(
        scraper_service=CupomScraperService(ThiagoRodrigoCupomClient()),
    )

    postagem_service = None
    if args.confirmar_envio:
        settings = get_settings()
        postagem_service = CupomPostagemService(
            TelegramClient(
                bot_token=settings.telegram_bot_token,
                chat_id=settings.telegram_chat_id,
            )
        )

    return CupomRotinaDiariaService(
        produto_update_service=produto_update_service,
        preview_runner=preview_runner,
        historico_service=CupomPostagemHistoricoService(),
        postagem_service=postagem_service,
    )


def _criar_produto_client(args: argparse.Namespace) -> ProdutoHtmlClient:
    if args.browser:
        return BrowserProdutoClient(
            user_data_dir=args.browser_perfil,
            headless=not args.browser_visivel,
            timeout_ms=args.browser_timeout,
            scrolls=args.browser_scrolls,
            delay_ms=args.browser_delay,
        )
    return MarketplaceProdutoClient()


def _imprimir_resultado(resultado: CupomRotinaDiariaResultado) -> None:
    print(f"Fontes carregadas: {resultado.produtos.total_fontes}")
    print(f"Produtos encontrados: {len(resultado.produtos.encontrados)}")
    print(f"Produtos finais salvos/usados: {len(resultado.produtos.produtos_finais)}")
    print(f"Cupons encontrados: {resultado.previews.total_cupons}")
    print(f"Produtos candidatos no preview: {resultado.previews.total_produtos}")
    print(f"Previews gerados: {resultado.previews.total_previews}")

    mensagens = [mensagem for _, mensagem in resultado.previews.previews]
    _imprimir_previews(mensagens)


def _imprimir_previews(mensagens: list[TelegramMessageDTO]) -> None:
    for index, mensagem in enumerate(mensagens, start=1):
        print()
        print(f"--- Preview {index} ---")
        print(f"Imagem: {mensagem.image_url}")
        print()
        print(mensagem.caption)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Atualiza produtos, gera previews de cupons e publica com confirmacao.",
    )
    parser.add_argument(
        "--fontes",
        type=Path,
        default=Path("data/fontes_produtos.json"),
        help="Caminho do JSON com fontes de produtos.",
    )
    parser.add_argument(
        "--produtos",
        type=Path,
        default=Path("data/produtos_candidatos.json"),
        help="Caminho do JSON de produtos candidatos.",
    )
    parser.add_argument(
        "--historico",
        type=Path,
        default=Path("data/cupom_postagens.json"),
        help="Caminho do JSON local com historico de posts de cupom.",
    )
    parser.add_argument(
        "--limite-por-fonte",
        type=int,
        default=5,
        help="Quantidade maxima de produtos aceitos por fonte.",
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
        "--manter-existentes",
        action="store_true",
        help="Mantem produtos ja cadastrados e substitui apenas duplicados encontrados.",
    )
    parser.add_argument(
        "--nao-salvar-produtos",
        dest="salvar_produtos",
        action="store_false",
        default=True,
        help="Nao atualiza o JSON de produtos antes de gerar previews.",
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


if __name__ == "__main__":
    main()
