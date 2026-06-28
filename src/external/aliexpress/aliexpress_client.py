from collections.abc import Iterable
from datetime import datetime
from typing import Any, cast

import httpx

from src.external.aliexpress.aliexpress_signature import gerar_assinatura

PRODUCT_FIELDS = ",".join(
    [
        "product_id",
        "sku_id",
        "product_title",
        "product_detail_url",
        "promotion_link",
        "product_main_image_url",
        "target_sale_price",
        "sale_price",
        "target_original_price",
        "original_price",
        "target_sale_price_currency",
        "sale_price_currency",
        "discount",
        "evaluate_rate",
        "latest_volume",
        "commission_rate",
        "hot_product_commission_rate",
        "first_level_category_name",
        "second_level_category_name",
        "shop_name",
        "promo_code_info",
    ]
)


class AliExpressClient:
    def __init__(
        self,
        app_key: str,
        app_secret: str,
        tracking_id: str,
        base_url: str,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.app_key = app_key
        self.app_secret = app_secret
        self.tracking_id = tracking_id
        self.base_url = base_url
        self.http_client = http_client

    async def buscar_hot_products(
        self,
        keywords: str | None = None,
        page_no: int = 1,
        page_size: int = 20,
        category_ids: str | None = None,
    ) -> dict[str, Any]:
        return await self._request(
            "aliexpress.affiliate.hotproduct.query",
            {
                "keywords": keywords,
                "category_ids": category_ids,
                "fields": PRODUCT_FIELDS,
                "page_no": page_no,
                "page_size": page_size,
                "target_currency": "BRL",
                "target_language": "PT",
                "tracking_id": self.tracking_id,
                "ship_to_country": "BR",
                "sort": "LAST_VOLUME_DESC",
            },
        )

    async def buscar_smart_match(
        self,
        keywords: str,
        page_no: int = 1,
        page_size: int = 20,
        device_id: str = "null",
    ) -> dict[str, Any]:
        return await self._request(
            "aliexpress.affiliate.product.smartmatch",
            {
                "keywords": keywords,
                "fields": PRODUCT_FIELDS,
                "page_no": page_no,
                "page_size": page_size,
                "target_currency": "BRL",
                "target_language": "PT",
                "tracking_id": self.tracking_id,
                "country": "BR",
                "device_id": device_id,
            },
        )

    async def gerar_link_afiliado(
        self,
        source_values: str | Iterable[str],
        promotion_link_type: int = 0,
    ) -> list[str]:
        if isinstance(source_values, str):
            source_value_param = source_values
        else:
            source_value_param = ",".join(source_values)

        resposta = await self._request(
            "aliexpress.affiliate.link.generate",
            {
                "promotion_link_type": promotion_link_type,
                "source_values": source_value_param,
                "tracking_id": self.tracking_id,
                "ship_to_country": "BR",
            },
        )
        response_payload = self._extrair_response_payload(resposta)
        promotion_links = (
            response_payload.get("resp_result", {}).get("result", {}).get("promotion_links", [])
        )
        links = self._normalizar_promotion_links(promotion_links)
        return [item["promotion_link"] for item in links if item.get("promotion_link")]

    async def _request(self, api_method: str, params: dict[str, Any]) -> dict[str, Any]:
        if not self.app_key or not self.app_secret:
            raise RuntimeError(
                "ALIEXPRESS_APP_KEY e ALIEXPRESS_APP_SECRET precisam estar configurados."
            )

        request_params = self._params_comuns(api_method) | {
            chave: valor for chave, valor in params.items() if valor not in (None, "")
        }
        request_params["sign"] = gerar_assinatura(self.app_secret, request_params)

        if self.http_client is not None:
            response = await self.http_client.get(self.base_url, params=request_params)
        else:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(self.base_url, params=request_params)

        response.raise_for_status()
        payload = cast(dict[str, Any], response.json())
        if "error_response" in payload:
            error = payload["error_response"]
            raise RuntimeError(f"Erro AliExpress: {error.get('code')} - {error.get('msg')}")

        response_payload = self._extrair_response_payload(payload)
        resp_result = response_payload.get("resp_result", {})
        resp_code = resp_result.get("resp_code")
        resp_msg = resp_result.get("resp_msg")
        if resp_code not in (None, 200, "200") and resp_msg != "The result is empty":
            raise RuntimeError(f"Erro AliExpress: {resp_code} - {resp_msg}")

        if payload.get("code") not in (None, "0", 0):
            raise RuntimeError(f"Erro AliExpress: {payload}")
        return payload

    @staticmethod
    def _extrair_response_payload(payload: dict[str, Any]) -> dict[str, Any]:
        for chave, valor in payload.items():
            if chave.endswith("_response") and isinstance(valor, dict):
                return valor
        return payload

    @staticmethod
    def _normalizar_promotion_links(valor: Any) -> list[dict[str, Any]]:
        if isinstance(valor, list):
            return [item for item in valor if isinstance(item, dict)]
        if isinstance(valor, dict):
            promotion_link = valor.get("promotion_link")
            if isinstance(promotion_link, list):
                return [item for item in promotion_link if isinstance(item, dict)]
            if isinstance(promotion_link, dict):
                return [promotion_link]
            if isinstance(valor.get("source_value"), str) and isinstance(promotion_link, str):
                return [valor]
        return []

    def _params_comuns(self, api_method: str) -> dict[str, str]:
        return {
            "app_key": self.app_key,
            "format": "json",
            "method": api_method,
            "sign_method": "sha256",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "v": "2.0",
        }
