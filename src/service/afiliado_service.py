from src.dto.oferta_dto import OfertaDTO
from src.external.aliexpress.aliexpress_client import AliExpressClient


class AfiliadoService:
    def __init__(self, aliexpress_client: AliExpressClient) -> None:
        self.aliexpress_client = aliexpress_client

    async def garantir_link_afiliado(self, oferta: OfertaDTO) -> OfertaDTO:
        if "s.click.aliexpress.com" in str(oferta.afiliado_url):
            return oferta

        links = await self.aliexpress_client.gerar_link_afiliado(str(oferta.produto.detalhe_url))
        if not links:
            return oferta
        return oferta.model_copy(update={"afiliado_url": links[0]})
