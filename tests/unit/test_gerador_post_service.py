from decimal import Decimal

import httpx
import pytest

from src.domain.marketplace import MarketplaceSlug
from src.dto.oferta_dto import OfertaDTO
from src.dto.produto_dto import ProdutoDTO
from src.service.gerador_post_service import GeradorPostService


def test_extrair_product_id_de_link_item_aliexpress() -> None:
    link = "https://pt.aliexpress.com/item/1005006915475056.html?spm=a2g0o"

    assert GeradorPostService.extrair_product_id(link) == "1005006915475056"


def test_extrair_product_id_de_query_string() -> None:
    link = "https://example.com/click?productIds=1005006915475056&foo=bar"

    assert GeradorPostService.extrair_product_id(link) == "1005006915475056"


def test_extrair_product_id_retorna_none_para_link_invalido() -> None:
    assert GeradorPostService.extrair_product_id("https://pt.aliexpress.com/store/123") is None


def test_detecta_link_afiliado_aliexpress() -> None:
    assert GeradorPostService.eh_link_afiliado_aliexpress(
        "https://s.click.aliexpress.com/e/_mLKibMJ"
    )


def test_detecta_link_shopee() -> None:
    assert GeradorPostService.eh_link_shopee("https://shopee.com.br/product/344381236/52953470536")
    assert GeradorPostService.eh_link_shopee("https://s.shopee.com.br/60PasE9F6j")


def test_extrair_shopee_ids_de_link_desktop() -> None:
    link = "https://shopee.com.br/product/344381236/52953470536?utm_source=an_123"

    assert GeradorPostService.extrair_shopee_ids(link) == (344381236, 52953470536)


def test_extrair_shopee_ids_de_link_mobile_resolvido() -> None:
    link = "https://shopee.com.br/opaanlp/344381236/52953470536?__mobile__=1"

    assert GeradorPostService.extrair_shopee_ids(link) == (344381236, 52953470536)


def _shopee_payload() -> dict:
    return {
        "data": {
            "productOfferV2": {
                "nodes": [
                    {
                        "itemId": "52953470536",
                        "shopId": "344381236",
                        "productName": "Hub USB-C 6 em 1",
                        "imageUrl": "https://example.com/hub.jpg",
                        "productLink": "https://shopee.com.br/product/344381236/52953470536",
                        "offerLink": "https://s.shopee.com.br/original",
                        "priceMin": "79.90",
                        "sales": "50",
                        "ratingStar": "4.8",
                        "commissionRate": "7.5%",
                        "shopName": "Loja Tech",
                    }
                ]
            }
        }
    }


@pytest.mark.asyncio
async def test_gerar_por_link_shopee_desktop_gera_short_link() -> None:
    class FakeShopeeClient:
        async def buscar_product_offers(
            self,
            keyword: str | None = None,
            shop_id: int | None = None,
            item_id: int | None = None,
            page: int = 1,
            limit: int = 20,
        ) -> dict:
            assert keyword is None
            assert shop_id == 344381236
            assert item_id == 52953470536
            assert page == 1
            assert limit == 1
            return _shopee_payload()

        async def gerar_short_link(self, origin_url: str, sub_id: str | None = None) -> str:
            assert origin_url == "https://shopee.com.br/product/344381236/52953470536"
            assert sub_id is None
            return "https://s.shopee.com.br/short"

    service = GeradorPostService(
        object(),  # type: ignore[arg-type]
        object(),  # type: ignore[arg-type]
        shopee_client=FakeShopeeClient(),  # type: ignore[arg-type]
    )

    oferta, mensagem = await service.gerar_por_link(
        "https://shopee.com.br/product/344381236/52953470536?utm_source=an_123"
    )

    assert oferta.produto.marketplace == MarketplaceSlug.SHOPEE
    assert oferta.produto.external_id == "344381236:52953470536"
    assert str(oferta.afiliado_url) == "https://s.shopee.com.br/short"
    assert "Hub USB-C 6 em 1" in mensagem.caption
    assert "https://s.shopee.com.br/short" in mensagem.caption


@pytest.mark.asyncio
async def test_gerar_por_link_shopee_afiliado_mantem_link_recebido() -> None:
    link_afiliado = "https://s.shopee.com.br/60PasE9F6j"

    class FakeShopeeClient:
        async def buscar_product_offers(
            self,
            keyword: str | None = None,
            shop_id: int | None = None,
            item_id: int | None = None,
            page: int = 1,
            limit: int = 20,
        ) -> dict:
            assert shop_id == 344381236
            assert item_id == 52953470536
            return _shopee_payload()

        async def gerar_short_link(self, origin_url: str, sub_id: str | None = None) -> str:
            raise AssertionError("Nao deve gerar novo link quando o link recebido ja e afiliado.")

    def handler(request: httpx.Request) -> httpx.Response:
        if str(request.url) == "https://shopee.com.br/product/344381236/52953470536":
            return httpx.Response(200)
        assert str(request.url) == link_afiliado
        return httpx.Response(
            302,
            headers={"location": "https://shopee.com.br/product/344381236/52953470536"},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        service = GeradorPostService(
            object(),  # type: ignore[arg-type]
            object(),  # type: ignore[arg-type]
            shopee_client=FakeShopeeClient(),  # type: ignore[arg-type]
            http_client=http_client,
        )

        oferta, mensagem = await service.gerar_por_link(link_afiliado)

    assert str(oferta.afiliado_url) == link_afiliado
    assert link_afiliado in mensagem.caption


@pytest.mark.asyncio
async def test_gerar_por_link_afiliado_mantem_link_recebido() -> None:
    link_afiliado = "https://s.click.aliexpress.com/e/_mLKibMJ"
    product_id = "1005006915475056"

    class FakeAliExpressClient:
        async def buscar_product_detail(self, received_product_id: str) -> dict:
            assert received_product_id == product_id
            return {}

    class FakeAfiliadoService:
        async def garantir_link_afiliado(self, oferta: OfertaDTO) -> OfertaDTO:
            raise AssertionError("Nao deve gerar novo link quando o link recebido ja e afiliado.")

    def handler(request: httpx.Request) -> httpx.Response:
        if str(request.url) == link_afiliado:
            return httpx.Response(
                302,
                headers={
                    "location": f"https://pt.aliexpress.com/item/{product_id}.html",
                },
            )
        assert str(request.url) == f"https://pt.aliexpress.com/item/{product_id}.html"
        return httpx.Response(200)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        service = GeradorPostService(
            FakeAliExpressClient(),  # type: ignore[arg-type]
            FakeAfiliadoService(),  # type: ignore[arg-type]
            http_client=http_client,
        )

        def fake_mapper(_: dict) -> list[OfertaDTO]:
            return [
                OfertaDTO(
                    produto=ProdutoDTO(
                        marketplace=MarketplaceSlug.ALIEXPRESS,
                        external_id=product_id,
                        titulo="Mouse gamer RGB",
                        detalhe_url=f"https://pt.aliexpress.com/item/{product_id}.html",
                        imagem_url="https://example.com/img.jpg",
                    ),
                    preco_atual=Decimal("99.90"),
                    afiliado_url="https://s.click.aliexpress.com/e/_outroLink",
                )
            ]

        import src.service.gerador_post_service as module

        original_mapper = module.mapear_resposta_aliexpress
        module.mapear_resposta_aliexpress = fake_mapper
        try:
            oferta, mensagem = await service.gerar_por_link(link_afiliado)
        finally:
            module.mapear_resposta_aliexpress = original_mapper

    assert str(oferta.afiliado_url) == link_afiliado
    assert link_afiliado in mensagem.caption
