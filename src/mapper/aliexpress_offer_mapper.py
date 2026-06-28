import re
from decimal import Decimal, InvalidOperation
from typing import Any, cast

from src.domain.marketplace import MarketplaceSlug
from src.dto.oferta_dto import OfertaDTO
from src.dto.produto_dto import ProdutoDTO
from src.external.aliexpress.aliexpress_dto import AliExpressProdutoRaw


def extrair_produtos(payload: dict[str, Any]) -> list[AliExpressProdutoRaw]:
    result = payload.get("resp_result", {}).get("result", {})
    produtos = result.get("products", [])
    if isinstance(produtos, dict):
        produtos = produtos.get("product", [])
    return [
        cast(AliExpressProdutoRaw, produto) for produto in produtos if isinstance(produto, dict)
    ]


def mapear_produto_aliexpress(produto_raw: AliExpressProdutoRaw) -> OfertaDTO:
    product_id = str(produto_raw.get("product_id") or produto_raw.get("sku_id") or "")
    titulo = str(produto_raw.get("product_title") or "").strip()
    detalhe_url = str(
        produto_raw.get("product_detail_url") or produto_raw.get("promotion_link") or ""
    )
    afiliado_url = str(produto_raw.get("promotion_link") or detalhe_url)
    categoria = _join_textos(
        produto_raw.get("first_level_category_name"),
        produto_raw.get("second_level_category_name"),
    )
    cupom = _extrair_cupom(produto_raw.get("promo_code_info"))

    return OfertaDTO(
        produto=ProdutoDTO(
            marketplace=MarketplaceSlug.ALIEXPRESS,
            external_id=product_id,
            titulo=titulo,
            detalhe_url=detalhe_url,
            imagem_url=produto_raw.get("product_main_image_url"),
            categoria=categoria,
            marca=produto_raw.get("shop_name"),
            raw_data=dict(produto_raw),
        ),
        preco_atual=_parse_decimal(
            produto_raw.get("target_sale_price") or produto_raw.get("sale_price") or "0"
        ),
        preco_original=_parse_decimal_optional(
            produto_raw.get("target_original_price") or produto_raw.get("original_price")
        ),
        moeda=str(
            produto_raw.get("target_sale_price_currency")
            or produto_raw.get("sale_price_currency")
            or "BRL"
        ),
        afiliado_url=afiliado_url,
        desconto_percentual=_parse_int_percent(produto_raw.get("discount")),
        cupom_codigo=cupom.get("codigo"),
        cupom_descricao=cupom.get("descricao"),
        volume_vendas=_parse_int(produto_raw.get("latest_volume")),
        avaliacao_percentual=_parse_int_percent(produto_raw.get("evaluate_rate")),
        comissao_percentual=_parse_decimal_optional(
            produto_raw.get("hot_product_commission_rate") or produto_raw.get("commission_rate")
        ),
        raw_data=dict(produto_raw),
    )


def mapear_resposta_aliexpress(payload: dict[str, Any]) -> list[OfertaDTO]:
    ofertas = []
    for produto in extrair_produtos(payload):
        if produto.get("product_id") and produto.get("product_title"):
            ofertas.append(mapear_produto_aliexpress(produto))
    return ofertas


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


def _extrair_cupom(valor: Any) -> dict[str, str | None]:
    if isinstance(valor, list) and valor:
        valor = valor[0]
    if not isinstance(valor, dict):
        return {"codigo": None, "descricao": None}

    codigo = valor.get("promo_code") or valor.get("generic_redemption_code")
    descricao = valor.get("code_promotionurl") or valor.get("long_title")
    return {
        "codigo": str(codigo).strip() if codigo else None,
        "descricao": str(descricao).strip() if descricao else None,
    }


def _join_textos(*valores: Any) -> str | None:
    textos = [str(valor).strip() for valor in valores if valor]
    return " / ".join(textos) if textos else None
