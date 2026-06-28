from dataclasses import dataclass

from src.domain.marketplace import MarketplaceSlug


@dataclass(frozen=True)
class Produto:
    marketplace: MarketplaceSlug
    external_id: str
    titulo: str
    detalhe_url: str
    imagem_url: str | None = None
    categoria: str | None = None
    marca: str | None = None
