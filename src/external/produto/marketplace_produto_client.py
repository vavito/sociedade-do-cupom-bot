import httpx


class MarketplaceProdutoClient:
    def __init__(self, http_client: httpx.AsyncClient | None = None) -> None:
        self.http_client = http_client

    async def buscar_html(self, url: str) -> str:
        headers = {
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126.0 Safari/537.36"
            ),
        }
        if self.http_client is not None:
            response = await self.http_client.get(url, headers=headers, follow_redirects=True)
        else:
            async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)

        response.raise_for_status()
        return response.text
