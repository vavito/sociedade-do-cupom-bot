from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, HttpUrl

from src.dto.cupom_dto import LojaCupom


class ProdutoCandidatoDTO(BaseModel):
    loja: LojaCupom
    external_id: str
    titulo: str
    url: HttpUrl | str
    preco: Decimal = Field(gt=0)
    imagem_url: HttpUrl | str | None = None
    categoria: str | None = None
    marca: str | None = None
    comissao_percentual: Decimal | None = None
    data_referencia: date | None = None
    raw_data: dict = Field(default_factory=dict)
