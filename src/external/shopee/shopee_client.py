import json
import time
from typing import Any, cast

import httpx

from src.external.shopee.shopee_signature import gerar_authorization_header

PRODUCT_OFFER_QUERY = """
query ProductOfferV2($keyword: String, $shopId: String, $itemId: String, $page: Int, $limit: Int) {
  productOfferV2(keyword: $keyword, shopId: $shopId, itemId: $itemId, page: $page, limit: $limit) {
    nodes {
      itemId
      shopId
      productName
      itemName
      imageUrl
      productLink
      offerLink
      priceMin
      priceMax
      price
      commissionRate
      commission
      sales
      ratingStar
      discount
      shopName
    }
    pageInfo {
      page
      limit
      hasNextPage
    }
  }
}
"""

SHOP_OFFER_QUERY = """
query ShopOfferV2($keyword: String, $page: Int, $limit: Int) {
  shopOfferV2(keyword: $keyword, page: $page, limit: $limit) {
    nodes {
      shopId
      shopName
      shopLink
      offerLink
      imageUrl
      ratingStar
      commissionRate
    }
    pageInfo {
      page
      limit
      hasNextPage
    }
  }
}
"""

GENERATE_SHORT_LINK_MUTATION = """
mutation GenerateShortLink($input: GenerateShortLinkInput!) {
  generateShortLink(input: $input) {
    shortLink
  }
}
"""


class ShopeeClient:
    def __init__(
        self,
        app_id: str,
        secret: str,
        base_url: str,
        sub_id: str | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.app_id = app_id
        self.secret = secret
        self.base_url = base_url
        self.sub_id = sub_id
        self.http_client = http_client

    async def buscar_product_offers(
        self,
        keyword: str | None = None,
        shop_id: str | None = None,
        item_id: str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> dict[str, Any]:
        return await self._request(
            PRODUCT_OFFER_QUERY,
            {
                "keyword": keyword,
                "shopId": shop_id,
                "itemId": item_id,
                "page": page,
                "limit": limit,
            },
        )

    async def buscar_shop_offers(
        self,
        keyword: str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> dict[str, Any]:
        return await self._request(
            SHOP_OFFER_QUERY,
            {
                "keyword": keyword,
                "page": page,
                "limit": limit,
            },
        )

    async def gerar_short_link(self, origin_url: str, sub_id: str | None = None) -> str | None:
        payload = await self._request(
            GENERATE_SHORT_LINK_MUTATION,
            {
                "input": {
                    "originUrl": origin_url,
                    "subIds": [sub_id or self.sub_id] if sub_id or self.sub_id else [],
                }
            },
        )
        short_link = payload.get("data", {}).get("generateShortLink", {}).get("shortLink")
        return str(short_link) if short_link else None

    async def _request(self, query: str, variables: dict[str, Any]) -> dict[str, Any]:
        if not self.app_id or not self.secret:
            raise RuntimeError("SHOPEE_APP_ID e SHOPEE_SECRET precisam estar configurados.")

        body = self._serializar_payload(
            {
                "query": query,
                "variables": self._remover_none(variables),
            }
        )
        timestamp = int(time.time())
        headers = {
            "Authorization": gerar_authorization_header(
                self.app_id,
                timestamp,
                body,
                self.secret,
            ),
            "Content-Type": "application/json",
        }

        if self.http_client is not None:
            response = await self.http_client.post(self.base_url, content=body, headers=headers)
        else:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(self.base_url, content=body, headers=headers)

        response.raise_for_status()
        payload = cast(dict[str, Any], response.json())
        if payload.get("errors"):
            raise RuntimeError(f"Erro Shopee: {payload['errors']}")
        return payload

    @staticmethod
    def _serializar_payload(payload: dict[str, Any]) -> str:
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

    @classmethod
    def _remover_none(cls, valor: Any) -> Any:
        if isinstance(valor, dict):
            return {
                chave: cls._remover_none(item) for chave, item in valor.items() if item is not None
            }
        if isinstance(valor, list):
            return [cls._remover_none(item) for item in valor if item is not None]
        return valor
