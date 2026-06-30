from datetime import datetime

from src.dto.cupom_dto import CupomDTO
from src.dto.cupom_produto_match_dto import CupomProdutoMatchDTO
from src.dto.produto_candidato_dto import ProdutoCandidatoDTO
from src.dto.telegram_message_dto import TelegramMessageDTO
from src.service.cupom_post_preview_service import CupomPostPreviewService
from src.service.cupom_produto_match_service import CupomProdutoMatchService
from src.service.politica_repost_produto_service import PoliticaRepostProdutoService


class CupomProdutoPreviewPipelineService:
    def __init__(
        self,
        match_service: CupomProdutoMatchService | None = None,
        preview_service: CupomPostPreviewService | None = None,
        repost_policy: PoliticaRepostProdutoService | None = None,
    ) -> None:
        self.match_service = match_service or CupomProdutoMatchService()
        self.preview_service = preview_service or CupomPostPreviewService()
        self.repost_policy = repost_policy or PoliticaRepostProdutoService()

    def gerar_previews(
        self,
        cupons: list[CupomDTO],
        produtos: list[ProdutoCandidatoDTO],
        postagens_por_produto: dict[str, list[datetime]],
        agora: datetime,
        limite: int = 10,
    ) -> list[tuple[CupomProdutoMatchDTO, TelegramMessageDTO]]:
        previews = []
        produtos_usados = set()

        for match in self.match_service.gerar_matches(cupons, produtos):
            chave_produto = self._chave_produto(match.produto)
            if chave_produto in produtos_usados:
                continue

            postagens = postagens_por_produto.get(chave_produto, [])
            if not self.repost_policy.pode_postar(postagens, agora):
                continue

            previews.append((match, self.preview_service.gerar(match)))
            produtos_usados.add(chave_produto)

            if len(previews) >= limite:
                break

        return previews

    @staticmethod
    def _chave_produto(produto: ProdutoCandidatoDTO) -> str:
        return f"{produto.loja}:{produto.external_id}"
