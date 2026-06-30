import json
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

from src.dto.produto_candidato_dto import ProdutoCandidatoDTO


class ProdutoCandidatoSeedService:
    def carregar_de_arquivo(
        self,
        caminho: str | Path,
        data_referencia: date | None = None,
    ) -> list[ProdutoCandidatoDTO]:
        payload = json.loads(Path(caminho).read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError("Arquivo de produtos candidatos precisa conter uma lista.")

        return [
            self._mapear_produto(item, data_referencia)
            for item in payload
            if isinstance(item, dict)
        ]

    def _mapear_produto(
        self,
        item: dict[str, Any],
        data_referencia: date | None,
    ) -> ProdutoCandidatoDTO:
        dados = dict(item)
        if data_referencia is not None and not dados.get("data_referencia"):
            dados["data_referencia"] = data_referencia

        if "preco" in dados:
            dados["preco"] = Decimal(str(dados["preco"]))
        if dados.get("comissao_percentual") is not None:
            dados["comissao_percentual"] = Decimal(str(dados["comissao_percentual"]))

        return ProdutoCandidatoDTO(**dados)
