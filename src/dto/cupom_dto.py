from datetime import date
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, Field, HttpUrl


class LojaCupom(StrEnum):
    AMAZON = "amazon"
    MERCADO_LIVRE = "mercado_livre"
    KABUM = "kabum"
    SHOPEE = "shopee"
    OUTRA = "outra"


class TipoDescontoCupom(StrEnum):
    PERCENTUAL = "percentual"
    VALOR_FIXO = "valor_fixo"
    FRETE_GRATIS = "frete_gratis"
    DESCONHECIDO = "desconhecido"


class CupomDTO(BaseModel):
    fonte: str
    loja: LojaCupom
    titulo: str
    descricao: str | None = None
    codigo: str | None = None
    data: date | None = None
    tipo: str | None = None
    link_resgate: HttpUrl | str | None = None
    desconto_tipo: TipoDescontoCupom = TipoDescontoCupom.DESCONHECIDO
    desconto_valor: Decimal | None = None
    valor_minimo: Decimal | None = None
    limite_desconto: Decimal | None = None
    somente_app: bool = False
    primeira_compra: bool = False
    exclusivo: bool = False
    categoria_hint: str | None = None
    raw_data: dict = Field(default_factory=dict)
