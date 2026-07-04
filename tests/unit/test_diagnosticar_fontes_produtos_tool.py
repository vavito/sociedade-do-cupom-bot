from argparse import Namespace
from datetime import date
from decimal import Decimal
from pathlib import Path

from src.dto.cupom_dto import LojaCupom
from src.dto.fonte_produto_dto import FonteProdutoDTO
from src.external.produto.browser_produto_client import BrowserProdutoClient
from src.external.produto.marketplace_produto_client import MarketplaceProdutoClient
from src.tools.diagnosticar_fontes_produtos import _criar_client, _filtrar_fontes, _parse_date


def test_parse_date() -> None:
    assert _parse_date("2026-07-01") == date(2026, 7, 1)


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


def criar_fonte(loja: LojaCupom, categoria: str) -> FonteProdutoDTO:
    return FonteProdutoDTO(
        loja=loja,
        categoria=categoria,
        url="https://example.com/busca",
        preco_minimo=Decimal("100"),
        preco_maximo=Decimal("1000"),
    )


def test_filtrar_fontes_por_loja_e_categoria() -> None:
    fontes = [
        criar_fonte(LojaCupom.AMAZON, "headset_fone"),
        criar_fonte(LojaCupom.MERCADO_LIVRE, "headset_fone"),
        criar_fonte(LojaCupom.AMAZON, "teclado"),
    ]

    filtradas = _filtrar_fontes(
        fontes,
        lojas=["amazon"],
        categorias=["headset_fone"],
    )

    assert filtradas == [fontes[0]]
