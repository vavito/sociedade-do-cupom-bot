import httpx
import pytest

from src.external.cupom.thiago_rodrigo_client import (
    AMAZON_CUPOM_URL,
    MERCADO_LIVRE_CUPOM_URL,
    ThiagoRodrigoCupomClient,
)


@pytest.mark.asyncio
async def test_buscar_html_amazon_usa_url_configurada() -> None:
    requests: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(str(request.url))
        assert "Mozilla/5.0" in request.headers["user-agent"]
        return httpx.Response(200, text="<html>amazon</html>")

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        html = await ThiagoRodrigoCupomClient(http_client).buscar_html_amazon()

    assert html == "<html>amazon</html>"
    assert requests == [AMAZON_CUPOM_URL]


@pytest.mark.asyncio
async def test_buscar_html_mercado_livre_usa_url_configurada() -> None:
    requests: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(str(request.url))
        return httpx.Response(200, text="<html>mercado livre</html>")

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        html = await ThiagoRodrigoCupomClient(http_client).buscar_html_mercado_livre()

    assert html == "<html>mercado livre</html>"
    assert requests == [MERCADO_LIVRE_CUPOM_URL]
