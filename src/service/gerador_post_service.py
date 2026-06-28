import re

import httpx

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
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.aliexpress_client = aliexpress_client
        self.afiliado_service = afiliado_service
        self.http_client = http_client

    async def gerar_por_link(self, link: str) -> tuple[OfertaDTO, TelegramMessageDTO]:
        link = link.strip()
        link_afiliado_recebido = self.eh_link_afiliado_aliexpress(link)
        product_id = self.extrair_product_id(link)

        if product_id is None and link_afiliado_recebido:
            product_id = await self._extrair_product_id_de_redirect(link)

        if product_id is None:
            raise ValueError("Link da AliExpress invalido.")

        payload = await self.aliexpress_client.buscar_product_detail(product_id)
        ofertas = mapear_resposta_aliexpress(payload)
        if not ofertas:
            raise ValueError("Nao foi possivel buscar dados do produto na AliExpress.")

        if link_afiliado_recebido:
            oferta = ofertas[0].model_copy(update={"afiliado_url": link})
        else:
            oferta = await self.afiliado_service.garantir_link_afiliado(ofertas[0])

        mensagem = mapear_oferta_para_telegram(oferta)
        if len(str(oferta.afiliado_url)) > 300:
            raise ValueError("Nao foi possivel gerar link curto de afiliado.")
        return oferta, mensagem

    @staticmethod
    def eh_link_afiliado_aliexpress(link: str) -> bool:
        return bool(re.search(r"https?://s\.click\.aliexpress\.com/e/", link))

    @staticmethod
    def extrair_product_id(link: str) -> str | None:
        match = re.search(r"(?:/item/|productIds=|product_id=)(\d{10,})", link)
        if match:
            return match.group(1)

        fallback = re.search(r"\b(\d{10,})\b", link)
        return fallback.group(1) if fallback else None

    async def _extrair_product_id_de_redirect(self, link: str) -> str | None:
        if self.http_client is not None:
            response = await self.http_client.get(link, follow_redirects=True)
        else:
            async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                response = await client.get(link)

        product_id = self.extrair_product_id(str(response.url))
        if product_id is not None:
            return product_id

        location = response.headers.get("location")
        if location:
            return self.extrair_product_id(location)
        return None
