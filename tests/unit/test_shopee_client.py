import json

import httpx
import pytest

from src.external.shopee.shopee_client import ShopeeClient


@pytest.mark.asyncio
async def test_buscar_product_offers_envia_graphql_assinado() -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["authorization"] = request.headers["authorization"]
        captured["payload"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(
            200,
            json={"data": {"productOfferV2": {"nodes": []}}},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = ShopeeClient(
            app_id="123",
            secret="secret",
            base_url="https://example.com/graphql",
            http_client=http_client,
        )
        payload = await client.buscar_product_offers(keyword="ssd", limit=5)

    assert payload == {"data": {"productOfferV2": {"nodes": []}}}
    assert captured["authorization"].startswith("SHA256 Credential=123, Timestamp=")
    assert "productOfferV2" in captured["payload"]["query"]
    assert captured["payload"]["variables"]["keyword"] == "ssd"
    assert captured["payload"]["variables"]["limit"] == 5
    assert "shopId" not in captured["payload"]["variables"]


@pytest.mark.asyncio
async def test_gerar_short_link_retorna_link() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"data": {"generateShortLink": {"shortLink": "https://s.shopee.com.br/abc"}}},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = ShopeeClient(
            app_id="123",
            secret="secret",
            base_url="https://example.com/graphql",
            sub_id="telegram",
            http_client=http_client,
        )

        assert await client.gerar_short_link("https://shopee.com.br/produto") == (
            "https://s.shopee.com.br/abc"
        )
