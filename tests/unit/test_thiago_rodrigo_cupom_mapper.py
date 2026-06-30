from datetime import date
from decimal import Decimal
from pathlib import Path

from src.dto.cupom_dto import LojaCupom
from src.mapper.thiago_rodrigo_cupom_mapper import mapear_cupons_thiago_rodrigo
from src.service.cupom_normalizer_service import CupomNormalizerService

FIXTURE = Path(__file__).parent.parent / "fixtures" / "thiago_rodrigo_cupons.html"


def test_mapear_cupons_thiago_rodrigo_extrai_codigo_e_metadados() -> None:
    html = FIXTURE.read_text(encoding="utf-8")

    cupons = mapear_cupons_thiago_rodrigo(
        html,
        LojaCupom.AMAZON,
        "https://thiagorodrigo.com.br/cupom-desconto-amazon-brasil/",
    )

    assert len(cupons) == 2
    assert cupons[0].loja == LojaCupom.AMAZON
    assert cupons[0].titulo == "Cupom Amazon de 10% de desconto"
    assert cupons[0].codigo == "CRAQUE10"
    assert cupons[0].data == date(2026, 6, 29)
    assert cupons[0].tipo == "Cupom"
    assert str(cupons[0].link_resgate) == "https://www.amazon.com.br/?tag=thiagorodrigosp-20"


def test_cupom_mapeado_pode_ser_normalizado() -> None:
    html = FIXTURE.read_text(encoding="utf-8")
    cupons = mapear_cupons_thiago_rodrigo(
        html,
        LojaCupom.AMAZON,
        "https://thiagorodrigo.com.br/cupom-desconto-amazon-brasil/",
    )

    normalizado = CupomNormalizerService().normalizar(cupons[0])

    assert normalizado.desconto_valor == Decimal("10")
    assert normalizado.valor_minimo == Decimal("250")
    assert normalizado.limite_desconto == Decimal("50")
