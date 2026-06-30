import json
from decimal import Decimal
from pathlib import Path
from typing import Any

from src.dto.fonte_produto_dto import FonteProdutoDTO


class FonteProdutoSeedService:
    def carregar_de_arquivo(self, caminho: str | Path) -> list[FonteProdutoDTO]:
        payload = json.loads(Path(caminho).read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError("Arquivo de fontes de produtos precisa conter uma lista.")

        return [self._mapear_fonte(item) for item in payload if isinstance(item, dict)]

    def _mapear_fonte(self, item: dict[str, Any]) -> FonteProdutoDTO:
        dados = dict(item)
        if dados.get("preco_minimo") is not None:
            dados["preco_minimo"] = Decimal(str(dados["preco_minimo"]))
        if dados.get("preco_maximo") is not None:
            dados["preco_maximo"] = Decimal(str(dados["preco_maximo"]))
        return FonteProdutoDTO(**dados)
