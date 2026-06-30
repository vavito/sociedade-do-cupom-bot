from pathlib import Path

import httpx
import pytest

from src.external.cupom.thiago_rodrigo_client import ThiagoRodrigoCupomClient
from src.service.cupom_scraper_service import CupomScraperService

FIXTURE = Path(__file__).parent.parent / "fixtures" / "thiago_rodrigo_cupons.html"


@pytest.mark.asyncio
async def test_buscar_cupons_amazon_processa_html_filtrado() -> None:
    html_fixture = FIXTURE.read_text(encoding="utf-8")

    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=html_fixture)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        service = CupomScraperService(ThiagoRodrigoCupomClient(http_client))
        cupons = await service.buscar_cupons_amazon()

    assert len(cupons) == 1
    assert cupons[0].codigo == "CRAQUE10"
    assert cupons[0].desconto_valor == 10
    assert cupons[0].valor_minimo == 250


@pytest.mark.asyncio
async def test_buscar_cupons_amazon_pode_retornar_sem_filtrar() -> None:
    html_fixture = FIXTURE.read_text(encoding="utf-8")

    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=html_fixture)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        service = CupomScraperService(ThiagoRodrigoCupomClient(http_client))
        cupons = await service.buscar_cupons_amazon(filtrar=False)

    assert [cupom.codigo for cupom in cupons] == ["CRAQUE10"]
