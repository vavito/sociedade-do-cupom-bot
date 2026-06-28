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
