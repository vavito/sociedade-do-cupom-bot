from src.service.gerador_post_service import GeradorPostService


def test_extrair_product_id_de_link_item_aliexpress() -> None:
    link = "https://pt.aliexpress.com/item/1005006915475056.html?spm=a2g0o"

    assert GeradorPostService.extrair_product_id(link) == "1005006915475056"


def test_extrair_product_id_de_query_string() -> None:
    link = "https://example.com/click?productIds=1005006915475056&foo=bar"

    assert GeradorPostService.extrair_product_id(link) == "1005006915475056"


def test_extrair_product_id_retorna_none_para_link_invalido() -> None:
    assert GeradorPostService.extrair_product_id("https://pt.aliexpress.com/store/123") is None
