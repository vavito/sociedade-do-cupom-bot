from datetime import date
from decimal import Decimal
import logging

from src.dto.cupom_dto import LojaCupom
from src.dto.fonte_produto_dto import FonteProdutoDTO
from src.service.produto_candidato_scraper_service import ProdutoCandidatoScraperService


class FakeMarketplaceProdutoClient:
    def __init__(self, html_por_url: dict[str, str]) -> None:
        self.html_por_url = html_por_url

    async def buscar_html(self, url: str) -> str:
        return self.html_por_url[url]


def criar_fonte(url: str = "https://example.com/headset") -> FonteProdutoDTO:
    return FonteProdutoDTO(
        loja=LojaCupom.AMAZON,
        categoria="headset_fone",
        url=url,
        preco_minimo=Decimal("100"),
        preco_maximo=Decimal("1000"),
        palavras_obrigatorias=["headset"],
        marcas_prioritarias=["redragon"],
    )


async def test_buscar_produtos_de_fontes_com_data_referencia() -> None:
    html = """
    <div data-component-type="s-search-result" data-asin="B001">
      <h2><span>Headset Gamer Redragon Zeus</span></h2>
      <a href="/dp/B001"></a>
      <span class="a-offscreen">R$ 299,90</span>
    </div>
    """
    service = ProdutoCandidatoScraperService(
        FakeMarketplaceProdutoClient({"https://example.com/headset": html})  # type: ignore[arg-type]
    )

    produtos = await service.buscar_produtos(
        [criar_fonte()],
        data_referencia=date(2026, 6, 30),
    )

    assert len(produtos) == 1
    assert produtos[0].external_id == "amazon-b001"
    assert produtos[0].data_referencia == date(2026, 6, 30)


async def test_deduplica_produtos_de_fontes_repetidas() -> None:
    html = """
    <div data-component-type="s-search-result" data-asin="B001">
      <h2><span>Headset Gamer Redragon Zeus</span></h2>
      <a href="/dp/B001"></a>
      <span class="a-offscreen">R$ 299,90</span>
    </div>
    """
    service = ProdutoCandidatoScraperService(
        FakeMarketplaceProdutoClient(
            {
                "https://example.com/headset-a": html,
                "https://example.com/headset-b": html,
            }
        )  # type: ignore[arg-type]
    )

    produtos = await service.buscar_produtos(
        [
            criar_fonte("https://example.com/headset-a"),
            criar_fonte("https://example.com/headset-b"),
        ]
    )

    assert len(produtos) == 1


async def test_avisa_quando_fonte_parece_bloqueada(caplog) -> None:  # type: ignore[no-untyped-def]
    html = "<html><title>Seguridad — Mercado Libre</title><body>captcha</body></html>"
    service = ProdutoCandidatoScraperService(
        FakeMarketplaceProdutoClient({"https://example.com/headset": html})  # type: ignore[arg-type]
    )

    with caplog.at_level(logging.WARNING):
        produtos = await service.buscar_produtos([criar_fonte()])

    assert produtos == []
    assert "possivel bloqueio ou pagina de seguranca" in caplog.text
