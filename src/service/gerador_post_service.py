import re

from src.dto.oferta_dto import OfertaDTO
from src.dto.telegram_message_dto import TelegramMessageDTO
from src.external.aliexpress.aliexpress_client import AliExpressClient
from src.mapper.aliexpress_offer_mapper import mapear_resposta_aliexpress
from src.mapper.telegram_message_mapper import mapear_oferta_para_telegram
from src.service.afiliado_service import AfiliadoService


class GeradorPostService:
    def __init__(
        self,
        aliexpress_client: AliExpressClient,
        afiliado_service: AfiliadoService,
    ) -> None:
        self.aliexpress_client = aliexpress_client
        self.afiliado_service = afiliado_service

    async def gerar_por_link(self, link: str) -> tuple[OfertaDTO, TelegramMessageDTO]:
        product_id = self.extrair_product_id(link)
        if product_id is None:
            raise ValueError("Link da AliExpress invalido.")

        payload = await self.aliexpress_client.buscar_product_detail(product_id)
        ofertas = mapear_resposta_aliexpress(payload)
        if not ofertas:
            raise ValueError("Nao foi possivel buscar dados do produto na AliExpress.")

        oferta = await self.afiliado_service.garantir_link_afiliado(ofertas[0])
        mensagem = mapear_oferta_para_telegram(oferta)
        if len(str(oferta.afiliado_url)) > 300:
            raise ValueError("Nao foi possivel gerar link curto de afiliado.")
        return oferta, mensagem

    @staticmethod
    def extrair_product_id(link: str) -> str | None:
        match = re.search(r"(?:/item/|productIds=|product_id=)(\d{10,})", link)
        if match:
            return match.group(1)

        fallback = re.search(r"\b(\d{10,})\b", link)
        return fallback.group(1) if fallback else None
