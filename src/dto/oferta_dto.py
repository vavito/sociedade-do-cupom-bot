from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from src.dto.produto_dto import ProdutoDTO


class OfertaDTO(BaseModel):
    produto: ProdutoDTO
    preco_atual: Decimal = Field(gt=0)
    moeda: str = "BRL"
    afiliado_url: HttpUrl | str
    preco_original: Decimal | None = None
    desconto_percentual: int | None = Field(default=None, ge=0, le=100)
    cupom_codigo: str | None = None
    cupom_descricao: str | None = None
    volume_vendas: int | None = None
    avaliacao_percentual: int | None = Field(default=None, ge=0, le=100)
    comissao_percentual: Decimal | None = None
    origem: str = "aliexpress"
    score: int = 0
    raw_data: dict = Field(default_factory=dict)

    model_config = ConfigDict(use_enum_values=True)
