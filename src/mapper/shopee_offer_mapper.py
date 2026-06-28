import re
from decimal import Decimal, InvalidOperation
from typing import Any, cast

from src.domain.marketplace import MarketplaceSlug
from src.dto.oferta_dto import OfertaDTO
from src.dto.produto_dto import ProdutoDTO
from src.external.shopee.shopee_dto import ShopeeProdutoRaw


def extrair_produtos_shopee(payload: dict[str, Any]) -> list[ShopeeProdutoRaw]:
    product_offer = payload.get("data", {}).get("productOfferV2", {})
    nodes = product_offer.get("nodes", [])
    return [cast(ShopeeProdutoRaw, item) for item in nodes if isinstance(item, dict)]


def mapear_produto_shopee(produto_raw: ShopeeProdutoRaw) -> OfertaDTO:
    item_id = str(produto_raw.get("itemId") or "")
    shop_id = str(produto_raw.get("shopId") or "")
    titulo = str(produto_raw.get("productName") or produto_raw.get("itemName") or "").strip()
    product_link = str(produto_raw.get("productLink") or produto_raw.get("offerLink") or "")
    afiliado_url = str(produto_raw.get("offerLink") or product_link)
    shop_name = str(produto_raw.get("shopName") or "").strip() or None

    return OfertaDTO(
        produto=ProdutoDTO(
            marketplace=MarketplaceSlug.SHOPEE,
            external_id=_join_id(shop_id, item_id),
            titulo=titulo,
            detalhe_url=product_link,
            imagem_url=produto_raw.get("imageUrl"),
            categoria=None,
            marca=shop_name,
            raw_data=dict(produto_raw),
        ),
        preco_atual=_parse_decimal(
            produto_raw.get("priceMin")
            or produto_raw.get("price")
            or produto_raw.get("priceMax")
            or "0"
        ),
        preco_original=None,
        moeda="BRL",
        afiliado_url=afiliado_url,
        desconto_percentual=_parse_int_percent(produto_raw.get("discount")),
        cupom_codigo=None,
        volume_vendas=_parse_int(produto_raw.get("sales")),
        avaliacao_percentual=_parse_rating_percent(produto_raw.get("ratingStar")),
        comissao_percentual=_parse_decimal_optional(produto_raw.get("commissionRate")),
        origem="shopee",
        raw_data=dict(produto_raw),
    )


def mapear_resposta_shopee(payload: dict[str, Any]) -> list[OfertaDTO]:
    ofertas = []
    for produto in extrair_produtos_shopee(payload):
        if (produto.get("itemId") or produto.get("productName")) and (
            produto.get("offerLink") or produto.get("productLink")
        ):
            ofertas.append(mapear_produto_shopee(produto))
    return ofertas


def _join_id(shop_id: str, item_id: str) -> str:
    if shop_id and item_id:
        return f"{shop_id}:{item_id}"
    return item_id or shop_id


def _parse_decimal(valor: Any) -> Decimal:
    parsed = _parse_decimal_optional(valor)
    return parsed if parsed is not None else Decimal("0")


def _parse_decimal_optional(valor: Any) -> Decimal | None:
    if valor in (None, ""):
        return None
    texto = str(valor).replace(",", ".")
    match = re.search(r"\d+(?:\.\d+)?", texto)
    if not match:
        return None
    try:
        return Decimal(match.group(0))
    except InvalidOperation:
        return None


def _parse_int(valor: Any) -> int | None:
    if valor in (None, ""):
        return None
    match = re.search(r"\d+", str(valor))
    return int(match.group(0)) if match else None


def _parse_int_percent(valor: Any) -> int | None:
    parsed = _parse_int(valor)
    if parsed is None:
        return None
    return max(0, min(parsed, 100))


def _parse_rating_percent(valor: Any) -> int | None:
    rating = _parse_decimal_optional(valor)
    if rating is None:
        return None
    if rating <= 5:
        return max(0, min(int(rating * 20), 100))
    return max(0, min(int(rating), 100))
