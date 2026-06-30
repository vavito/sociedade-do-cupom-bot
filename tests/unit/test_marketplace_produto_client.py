import httpx

from src.external.produto.marketplace_produto_client import MarketplaceProdutoClient


async def test_buscar_html_envia_headers_de_navegador() -> None:
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, text="<html>ok</html>")

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        html = await MarketplaceProdutoClient(http_client).buscar_html("https://example.com")

    assert html == "<html>ok</html>"
    assert requests[0].headers["user-agent"].startswith("Mozilla/5.0")
    assert "pt-BR" in requests[0].headers["accept-language"]
