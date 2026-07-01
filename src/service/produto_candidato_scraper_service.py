import logging
from datetime import date
from typing import Protocol

from src.dto.fonte_produto_dto import FonteProdutoDTO
from src.dto.produto_candidato_dto import ProdutoCandidatoDTO
from src.dto.produto_fonte_diagnostico_dto import ProdutoFonteDiagnosticoDTO
from src.mapper.produto_candidato_marketplace_mapper import diagnosticar_produtos_marketplace
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
        diagnosticos = await self.diagnosticar_fontes(
            fontes=fontes,
            data_referencia=data_referencia,
            limite_por_fonte=limite_por_fonte,
        )
        produtos_por_chave: dict[str, ProdutoCandidatoDTO] = {}

        for diagnostico in diagnosticos:
            for produto in diagnostico.produtos:
                produtos_por_chave.setdefault(
                    self.catalogo_service.chave_produto(produto),
                    produto,
                )

        return list(produtos_por_chave.values())

    async def diagnosticar_fontes(
        self,
        fontes: list[FonteProdutoDTO],
        data_referencia: date | None = None,
        limite_por_fonte: int = 10,
    ) -> list[ProdutoFonteDiagnosticoDTO]:
        diagnosticos = []

        for fonte in fontes:
            try:
                html = await self.client.buscar_html(str(fonte.url))
            except Exception as exc:
                logger.warning("Falha ao buscar fonte de produtos %s: %s", fonte.url, exc)
                diagnosticos.append(
                    ProdutoFonteDiagnosticoDTO(
                        fonte=fonte,
                        total_blocos=0,
                        produtos=[],
                        erro=str(exc),
                        motivo_sem_produtos="falha ao buscar html",
                    )
                )
                continue

            diagnostico = diagnosticar_produtos_marketplace(html, fonte)
            produtos = diagnostico.produtos[:limite_por_fonte]
            if not diagnostico.produtos:
                logger.warning(
                    "Fonte nao retornou produtos (%s): %s",
                    diagnostico.motivo_sem_produtos,
                    fonte.url,
                )

            produtos_datados = []
            for produto in produtos:
                if data_referencia is not None:
                    produto = produto.model_copy(update={"data_referencia": data_referencia})
                produtos_datados.append(produto)

            diagnosticos.append(
                ProdutoFonteDiagnosticoDTO(
                    fonte=fonte,
                    total_blocos=diagnostico.total_blocos,
                    produtos=produtos_datados,
                    rejeicoes=diagnostico.rejeicoes,
                    erro=diagnostico.erro,
                    motivo_sem_produtos=diagnostico.motivo_sem_produtos,
                )
            )

        return diagnosticos
