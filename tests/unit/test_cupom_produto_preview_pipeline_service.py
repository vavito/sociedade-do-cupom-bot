from datetime import date, datetime
from decimal import Decimal

from src.dto.cupom_dto import CupomDTO, LojaCupom, TipoDescontoCupom
from src.dto.produto_candidato_dto import ProdutoCandidatoDTO
from src.service.cupom_produto_preview_pipeline_service import (
    CupomProdutoPreviewPipelineService,
)


def criar_cupom(
    codigo: str,
    desconto_valor: Decimal,
    loja: LojaCupom = LojaCupom.AMAZON,
) -> CupomDTO:
    return CupomDTO(
        fonte="thiago_rodrigo",
        loja=loja,
        titulo=f"Cupom {codigo}",
        codigo=codigo,
        data=date(2026, 6, 30),
        desconto_tipo=TipoDescontoCupom.VALOR_FIXO,
        desconto_valor=desconto_valor,
        valor_minimo=Decimal("500"),
    )


def criar_produto(
    external_id: str,
    preco: Decimal = Decimal("1000"),
    loja: LojaCupom = LojaCupom.AMAZON,
) -> ProdutoCandidatoDTO:
    return ProdutoCandidatoDTO(
        loja=loja,
        external_id=external_id,
        titulo="Monitor gamer 24 polegadas",
        url=f"https://example.com/{external_id}",
        preco=preco,
        categoria="monitor",
        comissao_percentual=Decimal("5"),
        data_referencia=date(2026, 6, 30),
    )


def test_gera_previews_ordenados_por_score() -> None:
    previews = CupomProdutoPreviewPipelineService().gerar_previews(
        cupons=[
            criar_cupom("MENOR", Decimal("50")),
            criar_cupom("MAIOR", Decimal("100")),
        ],
        produtos=[criar_produto("monitor")],
        postagens_por_produto={},
        agora=datetime(2026, 6, 30, 10, 0),
    )

    assert len(previews) == 1
    assert previews[0][0].cupom.codigo == "MAIOR"
    assert "Cupom Amazon: MAIOR" in previews[0][1].caption


def test_bloqueia_produto_repostado_ha_menos_de_6h() -> None:
    previews = CupomProdutoPreviewPipelineService().gerar_previews(
        cupons=[criar_cupom("TECH100", Decimal("100"))],
        produtos=[criar_produto("monitor")],
        postagens_por_produto={
            "amazon:monitor": [datetime(2026, 6, 30, 9, 0)],
        },
        agora=datetime(2026, 6, 30, 14, 0),
    )

    assert previews == []


def test_permite_repost_depois_de_6h_antes_das_18h() -> None:
    previews = CupomProdutoPreviewPipelineService().gerar_previews(
        cupons=[criar_cupom("TECH100", Decimal("100"))],
        produtos=[criar_produto("monitor")],
        postagens_por_produto={
            "amazon:monitor": [datetime(2026, 6, 30, 9, 0)],
        },
        agora=datetime(2026, 6, 30, 15, 0),
    )

    assert len(previews) == 1


def test_respeita_limite_de_previews() -> None:
    previews = CupomProdutoPreviewPipelineService().gerar_previews(
        cupons=[criar_cupom("TECH100", Decimal("100"))],
        produtos=[criar_produto("monitor-1"), criar_produto("monitor-2")],
        postagens_por_produto={},
        agora=datetime(2026, 6, 30, 10, 0),
        limite=1,
    )

    assert len(previews) == 1
