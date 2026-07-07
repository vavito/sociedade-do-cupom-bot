from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from src.dto.cupom_dto import CupomDTO, LojaCupom, TipoDescontoCupom
from src.dto.cupom_produto_match_dto import CupomProdutoMatchDTO
from src.dto.fonte_produto_dto import FonteProdutoDTO
from src.dto.produto_candidato_dto import ProdutoCandidatoDTO
from src.dto.telegram_message_dto import TelegramMessageDTO
from src.service.cupom_postagem_service import CupomPostagemResultado
from src.service.cupom_preview_runner_service import CupomPreviewRunnerResultado
from src.service.cupom_rotina_diaria_service import CupomRotinaDiariaService
from src.service.produto_candidato_update_service import ProdutoCandidatoUpdateResultado


class FakeProdutoUpdateService:
    def __init__(self, resultado: ProdutoCandidatoUpdateResultado) -> None:
        self.resultado = resultado
        self.salvar: bool | None = None
        self.limite_por_fonte: int | None = None
        self.fontes: list[FonteProdutoDTO] | None = None

    async def atualizar(
        self,
        caminho_fontes: str | Path,
        caminho_saida: str | Path,
        data_referencia: date | None = None,
        limite_por_fonte: int = 10,
        manter_existentes: bool = False,
        salvar: bool = False,
    ) -> ProdutoCandidatoUpdateResultado:
        self.salvar = salvar
        self.limite_por_fonte = limite_por_fonte
        return self.resultado

    async def atualizar_por_fontes(
        self,
        fontes: list[FonteProdutoDTO],
        caminho_saida: str | Path,
        data_referencia: date | None = None,
        limite_por_fonte: int = 10,
        manter_existentes: bool = False,
        salvar: bool = False,
    ) -> ProdutoCandidatoUpdateResultado:
        self.fontes = fontes
        self.salvar = salvar
        self.limite_por_fonte = limite_por_fonte
        return self.resultado


class FakePreviewRunner:
    def __init__(self, resultado: CupomPreviewRunnerResultado) -> None:
        self.resultado = resultado
        self.postagens_por_produto: dict[str, list[datetime]] | None = None
        self.filtrar_cupons: bool | None = None

    async def gerar_previews(
        self,
        caminho_produtos: str | Path,
        data_referencia: date | None = None,
        postagens_por_produto: dict[str, list[datetime]] | None = None,
        agora: datetime | None = None,
        limite: int = 10,
        filtrar_cupons: bool = True,
    ) -> CupomPreviewRunnerResultado:
        self.postagens_por_produto = postagens_por_produto
        self.filtrar_cupons = filtrar_cupons
        return self.resultado


class FakeHistoricoService:
    def __init__(self) -> None:
        self.historico = {"amazon:produto-antigo": [datetime(2026, 7, 1, 8, 0)]}
        self.salvos: list[dict[str, list[datetime]]] = []

    def carregar_de_arquivo(self, caminho: str | Path) -> dict[str, list[datetime]]:
        return self.historico

    def registrar_postagem(
        self,
        postagens_por_produto: dict[str, list[datetime]],
        chave_produto: str,
        postado_em: datetime,
    ) -> dict[str, list[datetime]]:
        atualizado = {chave: list(datas) for chave, datas in postagens_por_produto.items()}
        atualizado.setdefault(chave_produto, []).append(postado_em)
        return atualizado

    def salvar_em_arquivo(
        self,
        caminho: str | Path,
        postagens_por_produto: dict[str, list[datetime]],
    ) -> None:
        self.salvos.append(postagens_por_produto)


class FakePostagemService:
    def __init__(self) -> None:
        self.mensagens: list[TelegramMessageDTO] = []

    async def publicar(self, mensagem: TelegramMessageDTO) -> CupomPostagemResultado:
        self.mensagens.append(mensagem)
        return CupomPostagemResultado(
            mensagem=mensagem,
            telegram_message_id=f"telegram-{len(self.mensagens)}",
        )


def criar_produto() -> ProdutoCandidatoDTO:
    return ProdutoCandidatoDTO(
        loja=LojaCupom.AMAZON,
        external_id="headset",
        titulo="Headset Havit",
        url="https://www.amazon.com.br/headset",
        preco=Decimal("199.90"),
        categoria="headset_fone",
    )


def criar_fonte() -> FonteProdutoDTO:
    return FonteProdutoDTO(
        loja=LojaCupom.MERCADO_LIVRE,
        categoria="teclado",
        url="https://lista.mercadolivre.com.br/teclado-mecanico",
    )


def criar_match(produto: ProdutoCandidatoDTO) -> CupomProdutoMatchDTO:
    return CupomProdutoMatchDTO(
        cupom=CupomDTO(
            fonte="thiago_rodrigo",
            loja=LojaCupom.AMAZON,
            titulo="Cupom Amazon",
            codigo="TECH50",
            desconto_tipo=TipoDescontoCupom.VALOR_FIXO,
            desconto_valor=Decimal("50"),
        ),
        produto=produto,
        desconto_estimado=Decimal("50"),
        preco_estimado=Decimal("149.90"),
        score=80,
        motivo="Produto do nicho",
    )


async def test_rotina_diaria_gera_preview_sem_postar_no_dry_run(tmp_path) -> None:  # type: ignore[no-untyped-def]
    produto = criar_produto()
    update_resultado = ProdutoCandidatoUpdateResultado(
        total_fontes=2,
        encontrados=[produto],
        produtos_finais=[produto],
    )
    preview_resultado = CupomPreviewRunnerResultado(
        total_cupons=1,
        total_produtos=1,
        previews=[(criar_match(produto), TelegramMessageDTO(image_url=None, caption="preview"))],
    )
    update_service = FakeProdutoUpdateService(update_resultado)
    preview_runner = FakePreviewRunner(preview_resultado)
    postagem_service = FakePostagemService()
    service = CupomRotinaDiariaService(
        produto_update_service=update_service,  # type: ignore[arg-type]
        preview_runner=preview_runner,  # type: ignore[arg-type]
        postagem_service=postagem_service,  # type: ignore[arg-type]
    )

    resultado = await service.executar(
        caminho_fontes=tmp_path / "fontes.json",
        caminho_produtos=tmp_path / "produtos.json",
        caminho_historico=tmp_path / "historico.json",
        limite_por_fonte=4,
        confirmar_envio=False,
    )

    assert update_service.salvar is True
    assert update_service.limite_por_fonte == 4
    assert resultado.produtos == update_resultado
    assert resultado.previews == preview_resultado
    assert resultado.postagens == []
    assert postagem_service.mensagens == []


async def test_rotina_diaria_usa_fontes_filtradas_quando_informadas(
    tmp_path,
) -> None:  # type: ignore[no-untyped-def]
    fonte = criar_fonte()
    produto = criar_produto()
    update_resultado = ProdutoCandidatoUpdateResultado(
        total_fontes=1,
        encontrados=[produto],
        produtos_finais=[produto],
    )
    preview_resultado = CupomPreviewRunnerResultado(
        total_cupons=0,
        total_produtos=1,
        previews=[],
    )
    update_service = FakeProdutoUpdateService(update_resultado)
    service = CupomRotinaDiariaService(
        produto_update_service=update_service,  # type: ignore[arg-type]
        preview_runner=FakePreviewRunner(preview_resultado),  # type: ignore[arg-type]
    )

    await service.executar(
        caminho_fontes=tmp_path / "fontes.json",
        caminho_produtos=tmp_path / "produtos.json",
        caminho_historico=tmp_path / "historico.json",
        limite_por_fonte=3,
        fontes=[fonte],
    )

    assert update_service.fontes == [fonte]
    assert update_service.limite_por_fonte == 3


async def test_rotina_diaria_publica_e_registra_historico_quando_confirmado(
    tmp_path,
) -> None:  # type: ignore[no-untyped-def]
    produto = criar_produto()
    mensagem = TelegramMessageDTO(
        image_url="https://www.amazon.com.br/banner.jpg",
        caption="post",
    )
    update_resultado = ProdutoCandidatoUpdateResultado(
        total_fontes=1,
        encontrados=[produto],
        produtos_finais=[produto],
    )
    preview_resultado = CupomPreviewRunnerResultado(
        total_cupons=1,
        total_produtos=1,
        previews=[(criar_match(produto), mensagem)],
    )
    update_service = FakeProdutoUpdateService(update_resultado)
    preview_runner = FakePreviewRunner(preview_resultado)
    historico_service = FakeHistoricoService()
    postagem_service = FakePostagemService()
    service = CupomRotinaDiariaService(
        produto_update_service=update_service,  # type: ignore[arg-type]
        preview_runner=preview_runner,  # type: ignore[arg-type]
        historico_service=historico_service,  # type: ignore[arg-type]
        postagem_service=postagem_service,  # type: ignore[arg-type]
    )

    resultado = await service.executar(
        caminho_fontes=tmp_path / "fontes.json",
        caminho_produtos=tmp_path / "produtos.json",
        caminho_historico=tmp_path / "historico.json",
        confirmar_envio=True,
        filtrar_cupons=False,
        agora=datetime(2026, 7, 1, 10, 0),
    )

    assert preview_runner.postagens_por_produto == historico_service.historico
    assert preview_runner.filtrar_cupons is False
    assert postagem_service.mensagens == [mensagem]
    assert resultado.postagens[0].telegram_message_id == "telegram-1"
    assert historico_service.salvos[-1]["amazon:headset"] == [datetime(2026, 7, 1, 10, 0)]
