import logging
from datetime import date

from src.dto.fonte_produto_dto import FonteProdutoDTO
from src.dto.produto_candidato_dto import ProdutoCandidatoDTO
from src.external.produto.marketplace_produto_client import MarketplaceProdutoClient
from src.mapper.produto_candidato_marketplace_mapper import mapear_produtos_marketplace
from src.service.produto_candidato_catalogo_service import ProdutoCandidatoCatalogoService

logger = logging.getLogger(__name__)


class ProdutoCandidatoScraperService:
    def __init__(
        self,
        client: MarketplaceProdutoClient,
        catalogo_service: ProdutoCandidatoCatalogoService | None = None,
    ) -> None:
        self.client = client
        self.catalogo_service = catalogo_service or ProdutoCandidatoCatalogoService()

    async def buscar_produtos(
        self,
        fontes: list[FonteProdutoDTO],
        data_referencia: date | None = None,
        limite_por_fonte: int = 10,
    ) -> list[ProdutoCandidatoDTO]:
        produtos_por_chave: dict[str, ProdutoCandidatoDTO] = {}

        for fonte in fontes:
            try:
                html = await self.client.buscar_html(str(fonte.url))
            except Exception as exc:
                logger.warning("Falha ao buscar fonte de produtos %s: %s", fonte.url, exc)
                continue

            produtos = mapear_produtos_marketplace(html, fonte)[:limite_por_fonte]
            for produto in produtos:
                if data_referencia is not None:
                    produto = produto.model_copy(update={"data_referencia": data_referencia})
                produtos_por_chave.setdefault(
                    self.catalogo_service.chave_produto(produto),
                    produto,
                )

        return list(produtos_por_chave.values())
