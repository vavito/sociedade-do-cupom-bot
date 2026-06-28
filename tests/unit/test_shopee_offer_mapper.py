from decimal import Decimal

from src.domain.marketplace import MarketplaceSlug
from src.mapper.shopee_offer_mapper import mapear_resposta_shopee


def test_mapear_resposta_shopee_para_oferta_dto() -> None:
    payload = {
        "data": {
            "productOfferV2": {
                "nodes": [
                    {
                        "itemId": "456",
                        "shopId": "123",
                        "productName": "SSD NVMe 1TB",
                        "imageUrl": "https://example.com/ssd.jpg",
                        "productLink": "https://shopee.com.br/product/123/456",
                        "offerLink": "https://s.shopee.com.br/abc",
                        "priceMin": "299.90",
                        "discount": "25%",
                        "sales": "1200",
                        "ratingStar": "4.8",
                        "commissionRate": "6.5%",
                        "shopName": "Loja Tech",
                    }
                ]
            }
        }
    }

    ofertas = mapear_resposta_shopee(payload)

    assert len(ofertas) == 1
    assert ofertas[0].produto.marketplace == MarketplaceSlug.SHOPEE
    assert ofertas[0].produto.external_id == "123:456"
    assert ofertas[0].produto.titulo == "SSD NVMe 1TB"
    assert ofertas[0].preco_atual == Decimal("299.90")
    assert ofertas[0].desconto_percentual == 25
    assert ofertas[0].volume_vendas == 1200
    assert ofertas[0].avaliacao_percentual == 96
