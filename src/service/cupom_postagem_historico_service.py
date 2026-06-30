import json
from datetime import datetime
from pathlib import Path
from typing import Any


class CupomPostagemHistoricoService:
    def carregar_de_arquivo(self, caminho: str | Path) -> dict[str, list[datetime]]:
        path = Path(caminho)
        if not path.exists():
            return {}

        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Historico de cupons precisa conter um objeto JSON.")

        return {
            str(chave): self._mapear_timestamps(valor)
            for chave, valor in payload.items()
            if isinstance(chave, str)
        }

    def registrar_postagem(
        self,
        postagens_por_produto: dict[str, list[datetime]],
        chave_produto: str,
        postado_em: datetime,
    ) -> dict[str, list[datetime]]:
        atualizadas = {chave: list(datas) for chave, datas in postagens_por_produto.items()}
        atualizadas.setdefault(chave_produto, []).append(postado_em)
        return atualizadas

    def salvar_em_arquivo(
        self,
        caminho: str | Path,
        postagens_por_produto: dict[str, list[datetime]],
    ) -> None:
        path = Path(caminho)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            chave: [data.isoformat(timespec="seconds") for data in datas]
            for chave, datas in sorted(postagens_por_produto.items())
        }
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def _mapear_timestamps(valor: Any) -> list[datetime]:
        if not isinstance(valor, list):
            return []
        return [datetime.fromisoformat(item) for item in valor if isinstance(item, str)]
