import json
from pathlib import Path

from src.dto.cupom_dto import LojaCupom
from src.dto.produto_candidato_dto import ProdutoCandidatoDTO
from src.service.produto_candidato_seed_service import ProdutoCandidatoSeedService


class ProdutoCandidatoCatalogoService:
    def __init__(self, seed_service: ProdutoCandidatoSeedService | None = None) -> None:
        self.seed_service = seed_service or ProdutoCandidatoSeedService()

    def listar(self, caminho: str | Path) -> list[ProdutoCandidatoDTO]:
        path = Path(caminho)
        if not path.exists():
            return []
        return self.seed_service.carregar_de_arquivo(path)

    def adicionar(
        self,
        caminho: str | Path,
        produto: ProdutoCandidatoDTO,
        substituir: bool = False,
    ) -> list[ProdutoCandidatoDTO]:
        produtos = self.listar(caminho)
        chave_nova = self.chave_produto(produto)
        indice_existente = self._buscar_indice(produtos, chave_nova)

        if indice_existente is not None:
            if not substituir:
                raise ValueError(f"Produto candidato ja existe: {chave_nova}")
            produtos[indice_existente] = produto
        else:
            produtos.append(produto)

        produtos = self._ordenar(produtos)
        self.salvar(caminho, produtos)
        return produtos

    def remover(
        self,
        caminho: str | Path,
        loja: LojaCupom,
        external_id: str,
    ) -> bool:
        produtos = self.listar(caminho)
        chave_removida = f"{loja}:{external_id}"
        restantes = [
            produto for produto in produtos if self.chave_produto(produto) != chave_removida
        ]

        if len(restantes) == len(produtos):
            return False

        self.salvar(caminho, restantes)
        return True

    def salvar(self, caminho: str | Path, produtos: list[ProdutoCandidatoDTO]) -> None:
        path = Path(caminho)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = [self._serializar(produto) for produto in self._ordenar(produtos)]
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def chave_produto(produto: ProdutoCandidatoDTO) -> str:
        return f"{produto.loja}:{produto.external_id}"

    @staticmethod
    def _buscar_indice(produtos: list[ProdutoCandidatoDTO], chave: str) -> int | None:
        for index, produto in enumerate(produtos):
            if ProdutoCandidatoCatalogoService.chave_produto(produto) == chave:
                return index
        return None

    @staticmethod
    def _ordenar(produtos: list[ProdutoCandidatoDTO]) -> list[ProdutoCandidatoDTO]:
        return sorted(produtos, key=lambda produto: (produto.loja, produto.external_id))

    @staticmethod
    def _serializar(produto: ProdutoCandidatoDTO) -> dict:
        dados = produto.model_dump(mode="json", exclude_none=False)
        if not dados.get("raw_data"):
            dados.pop("raw_data", None)
        return dados
