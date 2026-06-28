from decimal import Decimal

from src.mapper.aliexpress_offer_mapper import mapear_resposta_aliexpress


def test_mapear_resposta_aliexpress_para_oferta_dto() -> None:
    payload = {
        "resp_result": {
            "result": {
                "products": [
                    {
                        "product_id": "100500",
                        "product_title": "SSD NVMe 1TB",
                        "product_detail_url": "https://aliexpress.com/item/100500.html",
                        "promotion_link": "https://s.click.aliexpress.com/e/abc",
                        "product_main_image_url": "https://ae01.alicdn.com/kf/img.jpg",
                        "target_sale_price": "299.90",
                        "target_original_price": "399.90",
                        "target_sale_price_currency": "BRL",
                        "discount": "25%",
                        "evaluate_rate": "96%",
                        "latest_volume": "123",
                        "hot_product_commission_rate": "8%",
                        "first_level_category_name": "Computer",
                        "second_level_category_name": "SSD",
                        "promo_code_info": {"promo_code": "AEBR3"},
                    }
                ]
            }
        }
    }

    ofertas = mapear_resposta_aliexpress(payload)

    assert len(ofertas) == 1
    assert ofertas[0].produto.external_id == "100500"
    assert ofertas[0].produto.titulo == "SSD NVMe 1TB"
    assert ofertas[0].preco_atual == Decimal("299.90")
    assert ofertas[0].desconto_percentual == 25
    assert ofertas[0].cupom_codigo == "AEBR3"
