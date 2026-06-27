from decimal import Decimal

from src.domain.marketplace import MarketplaceSlug
from src.dto.oferta_dto import OfertaDTO
from src.dto.produto_dto import ProdutoDTO
from src.service.score_oferta_service import ScoreOfertaService


def test_calcular_score_considera_desconto_volume_avaliacao_cupom_e_comissao() -> None:
    oferta = OfertaDTO(
        produto=ProdutoDTO(
            marketplace=MarketplaceSlug.ALIEXPRESS,
            external_id="100",
            titulo="SSD NVMe 1TB",
            detalhe_url="https://example.com/p",
        ),
        preco_atual=Decimal("299"),
        afiliado_url="https://s.click.aliexpress.com/e/teste",
        desconto_percentual=35,
        volume_vendas=300,
        avaliacao_percentual=95,
        cupom_codigo="AEBR3",
        comissao_percentual=Decimal("8.5"),
    )

    assert ScoreOfertaService().calcular(oferta) == 93
