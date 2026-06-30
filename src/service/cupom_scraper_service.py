from src.dto.cupom_dto import CupomDTO, LojaCupom
from src.external.cupom.thiago_rodrigo_client import (
    AMAZON_CUPOM_URL,
    MERCADO_LIVRE_CUPOM_URL,
    ThiagoRodrigoCupomClient,
)
from src.mapper.thiago_rodrigo_cupom_mapper import mapear_cupons_thiago_rodrigo
from src.service.cupom_filter_service import CupomFilterService
from src.service.cupom_normalizer_service import CupomNormalizerService


class CupomScraperService:
    def __init__(
        self,
        client: ThiagoRodrigoCupomClient,
        normalizer: CupomNormalizerService | None = None,
        filtro: CupomFilterService | None = None,
    ) -> None:
        self.client = client
        self.normalizer = normalizer or CupomNormalizerService()
        self.filtro = filtro or CupomFilterService()

    async def buscar_cupons_amazon(self, filtrar: bool = True) -> list[CupomDTO]:
        html = await self.client.buscar_html_amazon()
        return self._processar_html(html, LojaCupom.AMAZON, AMAZON_CUPOM_URL, filtrar)

    async def buscar_cupons_mercado_livre(self, filtrar: bool = True) -> list[CupomDTO]:
        html = await self.client.buscar_html_mercado_livre()
        return self._processar_html(html, LojaCupom.MERCADO_LIVRE, MERCADO_LIVRE_CUPOM_URL, filtrar)

    async def buscar_cupons_iniciais(self, filtrar: bool = True) -> list[CupomDTO]:
        cupons = []
        cupons.extend(await self.buscar_cupons_amazon(filtrar=filtrar))
        cupons.extend(await self.buscar_cupons_mercado_livre(filtrar=filtrar))
        return cupons

    def _processar_html(
        self,
        html: str,
        loja: LojaCupom,
        source_url: str,
        filtrar: bool,
    ) -> list[CupomDTO]:
        cupons = mapear_cupons_thiago_rodrigo(html, loja, source_url)
        cupons = [cupom for cupom in cupons if cupom.loja == loja]
        normalizados = self.normalizer.normalizar_lista(cupons)
        return self.filtro.filtrar(normalizados) if filtrar else normalizados
