from dataclasses import dataclass


@dataclass(frozen=True)
class Cupom:
    codigo: str
    descricao: str | None = None
    valor: str | None = None
    minimo: str | None = None
