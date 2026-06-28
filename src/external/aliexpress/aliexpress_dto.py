from typing import Any, TypedDict


class AliExpressProdutoRaw(TypedDict, total=False):
    product_id: str
    sku_id: str
    product_title: str
    product_detail_url: str
    promotion_link: str
    product_main_image_url: str
    target_sale_price: str
    sale_price: str
    target_original_price: str
    original_price: str
    target_sale_price_currency: str
    sale_price_currency: str
    discount: str
    evaluate_rate: str
    latest_volume: str
    lastest_volume: str
    commission_rate: str
    hot_product_commission_rate: str
    first_level_category_name: str
    second_level_category_name: str
    shop_name: str
    promo_code_info: dict[str, Any]
