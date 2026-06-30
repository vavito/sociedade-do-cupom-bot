from datetime import date
from decimal import Decimal

from src.dto.cupom_dto import CupomDTO, LojaCupom, TipoDescontoCupom
from src.dto.produto_candidato_dto import ProdutoCandidatoDTO
from src.service.cupom_produto_match_service import CupomProdutoMatchService


def criar_cupom(
    loja: LojaCupom = LojaCupom.AMAZON,
    desconto_tipo: TipoDescontoCupom = TipoDescontoCupom.PERCENTUAL,
    desconto_valor: Decimal = Decimal("10"),
    valor_minimo: Decimal | None = Decimal("1000"),
    limite_desconto: Decimal | None = Decimal("100"),
    categoria_hint: str | None = None,
) -> CupomDTO:
    return CupomDTO(
        fonte="thiago_rodrigo",
        loja=loja,
        titulo="Cupom Amazon de 10% de desconto",
        descricao="Cupom para produtos selecionados.",
        codigo="TECH10",
        data=date(2026, 6, 29),
        desconto_tipo=desconto_tipo,
        desconto_valor=desconto_valor,
        valor_minimo=valor_minimo,
        limite_desconto=limite_desconto,
        categoria_hint=categoria_hint,
    )


def criar_produto(
    loja: LojaCupom = LojaCupom.AMAZON,
    external_id: str = "p1",
    preco: Decimal = Decimal("1200"),
    titulo: str = "Monitor gamer 27 polegadas",
    categoria: str | None = "informatica",
    comissao_percentual: Decimal | None = Decimal("8"),
) -> ProdutoCandidatoDTO:
    return ProdutoCandidatoDTO(
        loja=loja,
        external_id=external_id,
        titulo=titulo,
        url="https://example.com/produto",
        preco=preco,
        categoria=categoria,
        comissao_percentual=comissao_percentual,
        data_referencia=date(2026, 6, 29),
    )


def test_gera_match_com_desconto_limitado() -> None:
    match = CupomProdutoMatchService().gerar_match(criar_cupom(), criar_produto())

    assert match is not None
    assert match.desconto_estimado == Decimal("100.00")
    assert match.preco_estimado == Decimal("1100.00")
    assert match.score > 0


def test_rejeita_produto_abaixo_do_minimo_do_cupom() -> None:
    match = CupomProdutoMatchService().gerar_match(
        criar_cupom(valor_minimo=Decimal("1000")),
        criar_produto(preco=Decimal("999.99")),
    )

    assert match is None


def test_rejeita_loja_diferente() -> None:
    match = CupomProdutoMatchService().gerar_match(
        criar_cupom(loja=LojaCupom.AMAZON),
        criar_produto(loja=LojaCupom.MERCADO_LIVRE),
    )

    assert match is None


def test_rejeita_datas_de_referencia_diferentes() -> None:
    produto = criar_produto()
    produto = produto.model_copy(update={"data_referencia": date(2026, 6, 28)})

    match = CupomProdutoMatchService().gerar_match(criar_cupom(), produto)

    assert match is None


def test_rejeita_categoria_incompativel() -> None:
    match = CupomProdutoMatchService().gerar_match(
        criar_cupom(categoria_hint="smartphones", valor_minimo=None),
        criar_produto(titulo="Monitor gamer 27 polegadas"),
    )

    assert match is None


def test_ordena_matches_por_score() -> None:
    service = CupomProdutoMatchService()
    matches = service.gerar_matches(
        [criar_cupom()],
        [
            criar_produto(external_id="p1", preco=Decimal("1000")),
            criar_produto(external_id="p2", preco=Decimal("1500")),
        ],
    )

    assert len(matches) == 2
    assert matches[0].score >= matches[1].score
