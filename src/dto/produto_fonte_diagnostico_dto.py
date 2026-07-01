from dataclasses import dataclass, field

from src.dto.fonte_produto_dto import FonteProdutoDTO
from src.dto.produto_candidato_dto import ProdutoCandidatoDTO


@dataclass(frozen=True)
class ProdutoFonteDiagnosticoDTO:
    fonte: FonteProdutoDTO
    total_blocos: int
    produtos: list[ProdutoCandidatoDTO]
    rejeicoes: dict[str, int] = field(default_factory=dict)
    erro: str | None = None
    motivo_sem_produtos: str | None = None

    @property
    def total_aceitos(self) -> int:
        return len(self.produtos)
