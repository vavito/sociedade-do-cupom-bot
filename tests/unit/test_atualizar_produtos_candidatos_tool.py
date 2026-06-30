from argparse import Namespace
from datetime import date
from decimal import Decimal
from pathlib import Path

from src.dto.cupom_dto import LojaCupom
from src.dto.produto_candidato_dto import ProdutoCandidatoDTO
from src.external.produto.browser_produto_client import BrowserProdutoClient
from src.external.produto.marketplace_produto_client import MarketplaceProdutoClient
from src.service.produto_candidato_catalogo_service import ProdutoCandidatoCatalogoService
from src.tools.atualizar_produtos_candidatos import _combinar_produtos, _criar_client, _parse_date


def criar_produto(
    external_id: str,
    titulo: str,
    preco: Decimal,
) -> ProdutoCandidatoDTO:
    return ProdutoCandidatoDTO(
        loja=LojaCupom.AMAZON,
        external_id=external_id,
        titulo=titulo,
        url=f"https://www.amazon.com.br/{external_id}",
        preco=preco,
        categoria="headset_fone",
    )


def test_combinar_produtos_preserva_existentes_e_substitui_duplicados() -> None:
    existente = criar_produto("headset", "Headset antigo", Decimal("199.90"))
    novo = criar_produto("headset", "Headset novo", Decimal("249.90"))
    outro = criar_produto("teclado", "Teclado mecanico", Decimal("299.90"))

    produtos = _combinar_produtos(
        [existente],
        [novo, outro],
        ProdutoCandidatoCatalogoService(),
    )

    assert [produto.external_id for produto in produtos] == ["headset", "teclado"]
    assert produtos[0].titulo == "Headset novo"
    assert produtos[0].preco == Decimal("249.90")


def test_parse_date() -> None:
    assert _parse_date("2026-06-30") == date(2026, 6, 30)


def test_criar_client_http_por_padrao() -> None:
    client = _criar_client(
        Namespace(
            browser=False,
        )
    )

    assert isinstance(client, MarketplaceProdutoClient)


def test_criar_client_browser_quando_solicitado() -> None:
    client = _criar_client(
        Namespace(
            browser=True,
            browser_perfil=Path(".browser/teste"),
            browser_visivel=True,
            browser_timeout=30_000,
            browser_scrolls=5,
            browser_delay=250,
        )
    )

    assert isinstance(client, BrowserProdutoClient)
    assert client.user_data_dir == Path(".browser/teste")
    assert client.headless is False
    assert client.timeout_ms == 30_000
    assert client.scrolls == 5
    assert client.delay_ms == 250
