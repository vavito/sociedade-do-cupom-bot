import argparse
from datetime import date
from decimal import Decimal

from src.dto.cupom_dto import LojaCupom
from src.tools.produtos_candidatos import _construir_produto, _parse_decimal


def test_construir_produto_classifica_categoria_pelo_titulo() -> None:
    args = argparse.Namespace(
        loja="amazon",
        external_id="amazon-ryzen-5700",
        titulo="Processador AMD Ryzen 7 5700",
        url="https://www.amazon.com.br/produto",
        preco="1099,90",
        imagem_url=None,
        categoria=None,
        marca="AMD",
        comissao_percentual="4.5",
        data_referencia="2026-06-30",
    )

    produto = _construir_produto(args)

    assert produto.loja == LojaCupom.AMAZON
    assert produto.external_id == "amazon-ryzen-5700"
    assert produto.preco == Decimal("1099.90")
    assert produto.categoria == "processador"
    assert produto.comissao_percentual == Decimal("4.5")
    assert produto.data_referencia == date(2026, 6, 30)


def test_construir_produto_preserva_categoria_informada() -> None:
    args = argparse.Namespace(
        loja="mercado_livre",
        external_id="ml-controle",
        titulo="Controle sem fio",
        url="https://www.mercadolivre.com.br/produto",
        preco="199.90",
        imagem_url="https://example.com/image.jpg",
        categoria="acessorio",
        marca=None,
        comissao_percentual=None,
        data_referencia=None,
    )

    produto = _construir_produto(args)

    assert produto.loja == LojaCupom.MERCADO_LIVRE
    assert produto.categoria == "acessorio"
    assert produto.imagem_url == "https://example.com/image.jpg"
    assert produto.comissao_percentual is None
    assert produto.data_referencia is None


def test_parse_decimal_aceita_virgula() -> None:
    assert _parse_decimal("99,90") == Decimal("99.90")
