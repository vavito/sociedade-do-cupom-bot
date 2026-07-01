import asyncio
from contextlib import suppress
from pathlib import Path

from playwright.async_api import (
    BrowserContext,
    Page,
    async_playwright,
)
from playwright.async_api import (
    Error as PlaywrightError,
)
from playwright.async_api import (
    TimeoutError as PlaywrightTimeoutError,
)


class BrowserProdutoClient:
    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    )

    def __init__(
        self,
        user_data_dir: str | Path = ".browser/produtos",
        headless: bool = True,
        timeout_ms: int = 45_000,
        scrolls: int = 3,
        delay_ms: int = 800,
    ) -> None:
        self.user_data_dir = Path(user_data_dir)
        self.headless = headless
        self.timeout_ms = timeout_ms
        self.scrolls = scrolls
        self.delay_ms = delay_ms

    async def buscar_html(self, url: str) -> str:
        self.user_data_dir.mkdir(parents=True, exist_ok=True)
        async with async_playwright() as playwright:
            context = await playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.user_data_dir),
                headless=self.headless,
                locale="pt-BR",
                timezone_id="America/Sao_Paulo",
                viewport={"width": 1366, "height": 768},
                user_agent=self.USER_AGENT,
                extra_http_headers={"Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"},
            )
            try:
                page = await context.new_page()
                await self._navegar(page, url)
                return await self._obter_conteudo(page)
            finally:
                await self._fechar_contexto(context)

    async def _navegar(self, page: Page, url: str) -> None:
        page.set_default_timeout(self.timeout_ms)
        await page.goto(url, wait_until="domcontentloaded", timeout=self.timeout_ms)
        with suppress(PlaywrightTimeoutError):
            await page.wait_for_load_state("networkidle", timeout=min(self.timeout_ms, 10_000))
        await self._rolar_pagina(page)

    async def _obter_conteudo(self, page: Page) -> str:
        for tentativa in range(3):
            try:
                return await page.content()
            except PlaywrightError:
                if tentativa == 2:
                    raise
                await page.wait_for_timeout(self.delay_ms)
        return await page.content()

    async def _rolar_pagina(self, page: Page) -> None:
        for _ in range(self.scrolls):
            await page.mouse.wheel(0, 900)
            await page.wait_for_timeout(self.delay_ms)
        await asyncio.sleep(self.delay_ms / 1000)

    @staticmethod
    async def _fechar_contexto(context: BrowserContext) -> None:
        await context.close()
