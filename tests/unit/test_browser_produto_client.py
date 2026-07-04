from pathlib import Path

from playwright.async_api import Error as PlaywrightError

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


class FakeContentPage:
    def __init__(self) -> None:
        self.calls = 0
        self.waits: list[int] = []

    async def content(self) -> str:
        self.calls += 1
        if self.calls == 1:
            raise PlaywrightError("page is navigating")
        return "<html>ok</html>"

    async def wait_for_timeout(self, timeout_ms: int) -> None:
        self.waits.append(timeout_ms)


class FakeSecurityPage:
    def __init__(self) -> None:
        self.waits: list[int] = []
        self.load_states: list[str] = []
        self.reloads = 0
        self.content_calls = 0

    async def content(self) -> str:
        self.content_calls += 1
        return "<html>captchait security</html>"

    async def wait_for_timeout(self, timeout_ms: int) -> None:
        self.waits.append(timeout_ms)

    async def wait_for_load_state(self, state: str, timeout: int) -> None:
        self.load_states.append(state)

    async def reload(self, wait_until: str, timeout: int) -> None:
        self.reloads += 1


async def test_rolar_pagina_respeita_quantidade_de_scrolls() -> None:
    client = BrowserProdutoClient(scrolls=2, delay_ms=150)
    page = FakePage()

    await client._rolar_pagina(page)  # type: ignore[arg-type]

    assert page.mouse.wheels == [(0, 900), (0, 900)]
    assert page.waits == [150, 150]


async def test_obter_conteudo_tenta_novamente_quando_pagina_ainda_navega() -> None:
    client = BrowserProdutoClient(delay_ms=250)
    page = FakeContentPage()

    html = await client._obter_conteudo(page)  # type: ignore[arg-type]

    assert html == "<html>ok</html>"
    assert page.calls == 2
    assert page.waits == [250]


def test_browser_client_usa_perfil_persistente_local(tmp_path: Path) -> None:
    user_data_dir = tmp_path / "browser"
    client = BrowserProdutoClient(
        user_data_dir=user_data_dir,
        headless=False,
        security_wait_ms=120_000,
    )

    assert client.user_data_dir == user_data_dir
    assert client.headless is False
    assert client.timeout_ms == 45_000
    assert client.security_wait_ms == 120_000
    assert "Chrome/" in client.USER_AGENT
    assert "HeadlessChrome" not in client.USER_AGENT


def test_detecta_pagina_de_seguranca_com_captchait() -> None:
    assert BrowserProdutoClient._pagina_de_seguranca("<html>CaptchaIt</html>") is True
    assert BrowserProdutoClient._pagina_de_seguranca("<html>produto</html>") is False


async def test_aguardar_intervencao_seguranca_espera_e_recarrega() -> None:
    client = BrowserProdutoClient(security_wait_ms=5_000, timeout_ms=30_000)
    page = FakeSecurityPage()

    await client._aguardar_intervencao_seguranca(page)  # type: ignore[arg-type]

    assert page.waits == [5_000]
    assert page.load_states == ["networkidle", "networkidle"]
    assert page.reloads == 1
