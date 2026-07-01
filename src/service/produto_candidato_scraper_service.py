import logging
from datetime import date
from typing import Protocol

from src.dto.fonte_produto_dto import FonteProdutoDTO
from src.dto.produto_candidato_dto import ProdutoCandidatoDTO
from src.mapper.produto_candidato_marketplace_mapper import mapear_produtos_marketplace
from src.service.produto_candidato_catalogo_service import ProdutoCandidatoCatalogoService

logger = logging.getLogger(__name__)


class ProdutoHtmlClient(Protocol):
    async def buscar_html(self, url: str) -> str: ...


class ProdutoCandidatoScraperService:
    def __init__(
        self,
        client: ProdutoHtmlClient,
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
            if not produtos:
                logger.warning(
                    "Fonte nao retornou produtos (%s): %s",
                    self._motivo_sem_produtos(html),
                    fonte.url,
                )

            for produto in produtos:
                if data_referencia is not None:
                    produto = produto.model_copy(update={"data_referencia": data_referencia})
                produtos_por_chave.setdefault(
                    self.catalogo_service.chave_produto(produto),
                    produto,
                )

        return list(produtos_por_chave.values())

    @staticmethod
    def _motivo_sem_produtos(html: str) -> str:
        texto = html.casefold()
        indicadores_bloqueio = [
            "seguridad",
            "captcha",
            "robot",
            "automated",
            "hubo un error accediendo",
            "service unavailable",
        ]
        if any(indicador in texto for indicador in indicadores_bloqueio):
            return "possivel bloqueio ou pagina de seguranca"
        return "nenhum card parseavel"
