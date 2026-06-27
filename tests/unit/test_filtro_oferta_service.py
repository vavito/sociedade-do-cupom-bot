from decimal import Decimal

from src.domain.marketplace import MarketplaceSlug
from src.dto.oferta_dto import OfertaDTO
from src.dto.produto_dto import ProdutoDTO
from src.service.filtro_oferta_service import FiltroOfertaService


def criar_oferta(titulo: str, categoria: str | None = None) -> OfertaDTO:
    return OfertaDTO(
        produto=ProdutoDTO(
            marketplace=MarketplaceSlug.ALIEXPRESS,
            external_id="100",
            titulo=titulo,
            detalhe_url="https://example.com/p",
            imagem_url="https://example.com/i.jpg",
            categoria=categoria,
        ),
        preco_atual=Decimal("199.90"),
        afiliado_url="https://s.click.aliexpress.com/e/teste",
    )


def test_oferta_elegivel_quando_produto_e_do_nicho_tech() -> None:
    service = FiltroOfertaService()

    assert service.oferta_elegivel(criar_oferta("SSD NVMe Kingston 1TB"))


def test_oferta_bloqueada_quando_tem_palavra_fora_do_nicho() -> None:
    service = FiltroOfertaService()

    assert not service.oferta_elegivel(criar_oferta("Capa de celular gamer"))
