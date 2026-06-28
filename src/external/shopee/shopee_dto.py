from typing import Any, TypedDict


class ShopeeProdutoRaw(TypedDict, total=False):
    itemId: str
    shopId: str
    productName: str
    itemName: str
    imageUrl: str
    productLink: str
    offerLink: str
    priceMin: str
    priceMax: str
    price: str
    commissionRate: str
    commission: str
    sales: str
    ratingStar: str
    discount: str
    shopName: str
    raw: dict[str, Any]
