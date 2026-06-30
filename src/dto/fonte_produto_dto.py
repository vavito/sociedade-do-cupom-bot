from decimal import Decimal

from pydantic import BaseModel, Field, HttpUrl

from src.dto.cupom_dto import LojaCupom


class FonteProdutoDTO(BaseModel):
    loja: LojaCupom
    categoria: str
    url: HttpUrl | str
    preco_minimo: Decimal | None = Field(default=None, ge=0)
    preco_maximo: Decimal | None = Field(default=None, gt=0)
    palavras_obrigatorias: list[str] = Field(default_factory=list)
    palavras_bloqueadas: list[str] = Field(default_factory=list)
    marcas_prioritarias: list[str] = Field(default_factory=list)
    marcas_bloqueadas: list[str] = Field(default_factory=list)
    limite_por_marca: int | None = Field(default=None, gt=0)
    ignorar_patrocinados: bool = True
