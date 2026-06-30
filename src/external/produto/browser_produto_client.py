import asyncio
from pathlib import Path

from playwright.async_api import BrowserContext, Page, TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright


class BrowserProdutoClient:
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
            )
            try:
                page = await context.new_page()
                await self._navegar(page, url)
                return await page.content()
            finally:
                await self._fechar_contexto(context)

    async def _navegar(self, page: Page, url: str) -> None:
        page.set_default_timeout(self.timeout_ms)
        await page.goto(url, wait_until="domcontentloaded", timeout=self.timeout_ms)
        try:
            await page.wait_for_load_state("networkidle", timeout=min(self.timeout_ms, 10_000))
        except PlaywrightTimeoutError:
            pass
        await self._rolar_pagina(page)

    async def _rolar_pagina(self, page: Page) -> None:
        for _ in range(self.scrolls):
            await page.mouse.wheel(0, 900)
            await page.wait_for_timeout(self.delay_ms)
        await asyncio.sleep(self.delay_ms / 1000)

    @staticmethod
    async def _fechar_contexto(context: BrowserContext) -> None:
        await context.close()
