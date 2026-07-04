from argparse import Namespace
from datetime import date
from pathlib import Path

from src.external.produto.browser_produto_client import BrowserProdutoClient
from src.external.produto.marketplace_produto_client import MarketplaceProdutoClient
from src.tools.atualizar_produtos_candidatos import _criar_client, _parse_date


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
            browser_espera_seguranca=60_000,
        )
    )

    assert isinstance(client, BrowserProdutoClient)
    assert client.user_data_dir == Path(".browser/teste")
    assert client.headless is False
    assert client.timeout_ms == 30_000
    assert client.scrolls == 5
    assert client.delay_ms == 250
    assert client.security_wait_ms == 60_000
