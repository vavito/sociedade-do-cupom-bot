from src.dto.cupom_dto import CupomDTO, LojaCupom
from src.service.cupom_filter_service import CupomFilterService


def criar_cupom(
    loja: LojaCupom,
    titulo: str,
    descricao: str | None = None,
    categoria_hint: str | None = None,
) -> CupomDTO:
    return CupomDTO(
        fonte="thiago_rodrigo",
        loja=loja,
        titulo=titulo,
        descricao=descricao,
        codigo="TECH10",
        categoria_hint=categoria_hint,
    )


def test_aceita_cupom_generico_de_amazon() -> None:
    cupom = criar_cupom(
        LojaCupom.AMAZON,
        "Cupom Amazon de R$ 100 de desconto",
        "Cupom para compras selecionadas acima de R$ 999.",
    )

    assert CupomFilterService().cupom_elegivel(cupom)


def test_aceita_cupom_tech_do_mercado_livre() -> None:
    cupom = criar_cupom(
        LojaCupom.MERCADO_LIVRE,
        "Cupom Mercado Livre para notebook gamer",
        categoria_hint="informatica",
    )

    assert CupomFilterService().cupom_elegivel(cupom)


def test_aceita_cupom_de_acessorio_do_nicho() -> None:
    cupom = criar_cupom(
        LojaCupom.MERCADO_LIVRE,
        "Cupom para suporte articulado de monitor",
        categoria_hint=None,
    )

    assert CupomFilterService().cupom_elegivel(cupom)


def test_bloqueia_cupom_fora_do_nicho() -> None:
    cupom = criar_cupom(
        LojaCupom.MERCADO_LIVRE,
        "Moda com 18% de desconto no Mercado Livre",
        categoria_hint="moda",
    )

    assert not CupomFilterService().cupom_elegivel(cupom)
