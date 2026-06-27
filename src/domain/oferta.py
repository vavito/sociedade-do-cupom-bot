from dataclasses import dataclass
from decimal import Decimal

from src.domain.cupom import Cupom
from src.domain.produto import Produto


@dataclass(frozen=True)
class Oferta:
    produto: Produto
    preco_atual: Decimal
    moeda: str
    afiliado_url: str
    preco_original: Decimal | None = None
    desconto_percentual: int | None = None
    cupom: Cupom | None = None
    score: int = 0
