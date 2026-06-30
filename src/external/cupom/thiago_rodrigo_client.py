import httpx

AMAZON_CUPOM_URL = "https://thiagorodrigo.com.br/cupom-desconto-amazon-brasil/"
MERCADO_LIVRE_CUPOM_URL = "https://thiagorodrigo.com.br/cupom-desconto-mercado-livre/"


class ThiagoRodrigoCupomClient:
    def __init__(self, http_client: httpx.AsyncClient | None = None) -> None:
        self.http_client = http_client

    async def buscar_html_amazon(self) -> str:
        return await self.buscar_html(AMAZON_CUPOM_URL)

    async def buscar_html_mercado_livre(self) -> str:
        return await self.buscar_html(MERCADO_LIVRE_CUPOM_URL)

    async def buscar_html(self, url: str) -> str:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126.0 Safari/537.36"
            )
        }
        if self.http_client is not None:
            response = await self.http_client.get(url, headers=headers)
        else:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url, headers=headers)

        response.raise_for_status()
        return response.text
