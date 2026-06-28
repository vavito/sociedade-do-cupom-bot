import re

import httpx

from src.dto.oferta_dto import OfertaDTO
from src.dto.telegram_message_dto import TelegramMessageDTO
from src.external.aliexpress.aliexpress_client import AliExpressClient
from src.external.shopee.shopee_client import ShopeeClient
from src.mapper.aliexpress_offer_mapper import mapear_resposta_aliexpress
from src.mapper.shopee_offer_mapper import mapear_resposta_shopee
from src.mapper.telegram_message_mapper import mapear_oferta_para_telegram
from src.service.afiliado_service import AfiliadoService


class GeradorPostService:
    def __init__(
        self,
        aliexpress_client: AliExpressClient,
        afiliado_service: AfiliadoService,
        shopee_client: ShopeeClient | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.aliexpress_client = aliexpress_client
        self.afiliado_service = afiliado_service
        self.shopee_client = shopee_client
        self.http_client = http_client

    async def gerar_por_link(self, link: str) -> tuple[OfertaDTO, TelegramMessageDTO]:
        link = link.strip()
        if self.eh_link_shopee(link):
            return await self._gerar_shopee_por_link(link)

        return await self._gerar_aliexpress_por_link(link)

    async def _gerar_aliexpress_por_link(self, link: str) -> tuple[OfertaDTO, TelegramMessageDTO]:
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

    async def _gerar_shopee_por_link(self, link: str) -> tuple[OfertaDTO, TelegramMessageDTO]:
        if self.shopee_client is None:
            raise ValueError("Cliente da Shopee nao configurado.")

        link_afiliado_recebido = self.eh_link_afiliado_shopee(link)
        ids = self.extrair_shopee_ids(link)

        if ids is None and link_afiliado_recebido:
            ids = await self._extrair_shopee_ids_de_redirect(link)

        if ids is None:
            raise ValueError("Link da Shopee invalido.")

        shop_id, item_id = ids
        payload = await self.shopee_client.buscar_product_offers(
            shop_id=shop_id,
            item_id=item_id,
            limit=1,
        )
        ofertas = mapear_resposta_shopee(payload)
        if not ofertas:
            raise ValueError("Nao foi possivel buscar dados do produto na Shopee.")

        oferta = ofertas[0]
        if link_afiliado_recebido:
            oferta = oferta.model_copy(update={"afiliado_url": link})
        else:
            short_link = await self.shopee_client.gerar_short_link(str(oferta.produto.detalhe_url))
            if short_link:
                oferta = oferta.model_copy(update={"afiliado_url": short_link})

        mensagem = mapear_oferta_para_telegram(oferta)
        if len(str(oferta.afiliado_url)) > 300:
            raise ValueError("Nao foi possivel gerar link curto de afiliado.")
        return oferta, mensagem

    @staticmethod
    def eh_link_afiliado_aliexpress(link: str) -> bool:
        return bool(re.search(r"https?://s\.click\.aliexpress\.com/e/", link))

    @staticmethod
    def eh_link_shopee(link: str) -> bool:
        return bool(re.search(r"https?://(?:s\.|(?:[\w-]+\.)?)shopee\.com\.br/", link))

    @staticmethod
    def eh_link_afiliado_shopee(link: str) -> bool:
        return bool(re.search(r"https?://s\.shopee\.com\.br/", link))

    @staticmethod
    def extrair_product_id(link: str) -> str | None:
        match = re.search(r"(?:/item/|productIds=|product_id=)(\d{10,})", link)
        if match:
            return match.group(1)

        fallback = re.search(r"\b(\d{10,})\b", link)
        return fallback.group(1) if fallback else None

    @staticmethod
    def extrair_shopee_ids(link: str) -> tuple[int, int] | None:
        patterns = [
            r"/product/(\d+)/(\d+)",
            r"-i\.(\d+)\.(\d+)",
            r"shopee\.com\.br/[^/?#]+/(\d{6,})/(\d{6,})",
            r"[?&]shop(?:I|_i)?d=(\d+).*?[?&]item(?:I|_i)?d=(\d+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, link)
            if match:
                return int(match.group(1)), int(match.group(2))
        return None

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

    async def _extrair_shopee_ids_de_redirect(self, link: str) -> tuple[int, int] | None:
        if self.http_client is not None:
            response = await self.http_client.get(link, follow_redirects=True)
        else:
            async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                response = await client.get(link)

        ids = self.extrair_shopee_ids(str(response.url))
        if ids is not None:
            return ids

        location = response.headers.get("location")
        if location:
            return self.extrair_shopee_ids(location)
        return None
