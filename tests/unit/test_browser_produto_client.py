from pathlib import Path

from src.external.produto.browser_produto_client import BrowserProdutoClient


class FakeMouse:
    def __init__(self) -> None:
        self.wheels: list[tuple[int, int]] = []

    async def wheel(self, delta_x: int, delta_y: int) -> None:
        self.wheels.append((delta_x, delta_y))


class FakePage:
    def __init__(self) -> None:
        self.mouse = FakeMouse()
        self.waits: list[int] = []

    async def wait_for_timeout(self, timeout_ms: int) -> None:
        self.waits.append(timeout_ms)


async def test_rolar_pagina_respeita_quantidade_de_scrolls() -> None:
    client = BrowserProdutoClient(scrolls=2, delay_ms=150)
    page = FakePage()

    await client._rolar_pagina(page)  # type: ignore[arg-type]

    assert page.mouse.wheels == [(0, 900), (0, 900)]
    assert page.waits == [150, 150]


def test_browser_client_usa_perfil_persistente_local(tmp_path: Path) -> None:
    user_data_dir = tmp_path / "browser"
    client = BrowserProdutoClient(user_data_dir=user_data_dir, headless=False)

    assert client.user_data_dir == user_data_dir
    assert client.headless is False
    assert client.timeout_ms == 45_000
