from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from src.domain.marketplace import MarketplaceSlug


class ProdutoDTO(BaseModel):
    marketplace: MarketplaceSlug
    external_id: str
    titulo: str
    detalhe_url: HttpUrl | str
    imagem_url: HttpUrl | str | None = None
    categoria: str | None = None
    marca: str | None = None
    raw_data: dict = Field(default_factory=dict)

    model_config = ConfigDict(use_enum_values=True)
