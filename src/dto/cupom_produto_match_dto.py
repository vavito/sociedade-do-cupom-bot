from decimal import Decimal

from pydantic import BaseModel

from src.dto.cupom_dto import CupomDTO
from src.dto.produto_candidato_dto import ProdutoCandidatoDTO


class CupomProdutoMatchDTO(BaseModel):
    cupom: CupomDTO
    produto: ProdutoCandidatoDTO
    desconto_estimado: Decimal
    preco_estimado: Decimal
    score: int
    motivo: str
