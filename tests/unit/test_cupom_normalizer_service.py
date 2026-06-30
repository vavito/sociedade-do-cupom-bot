from datetime import date
from decimal import Decimal

from src.dto.cupom_dto import CupomDTO, LojaCupom, TipoDescontoCupom
from src.service.cupom_normalizer_service import CupomNormalizerService


def test_normaliza_cupom_percentual_com_minimo_e_limite() -> None:
    cupom = CupomDTO(
        fonte="thiago_rodrigo",
        loja=LojaCupom.AMAZON,
        titulo="Cupom Amazon de 10% de desconto",
        descricao="Pague menos 10% comprando acima de R$ 250 com limite de R$ 50 OFF.",
        codigo=" craque10 ",
        data=date(2026, 6, 29),
    )

    normalizado = CupomNormalizerService().normalizar(cupom)

    assert normalizado.codigo == "CRAQUE10"
    assert normalizado.desconto_tipo == TipoDescontoCupom.PERCENTUAL
    assert normalizado.desconto_valor == Decimal("10")
    assert normalizado.valor_minimo == Decimal("250")
    assert normalizado.limite_desconto == Decimal("50")


def test_normaliza_flags_e_categoria() -> None:
    cupom = CupomDTO(
        fonte="thiago_rodrigo",
        loja=LojaCupom.MERCADO_LIVRE,
        titulo="Cupom exclusivo para notebook gamer",
        descricao="Somente aplicativo e primeira compra.",
        codigo="NOTE15",
    )

    normalizado = CupomNormalizerService().normalizar(cupom)

    assert normalizado.somente_app
    assert normalizado.primeira_compra
    assert normalizado.exclusivo
    assert normalizado.categoria_hint == "informatica"
