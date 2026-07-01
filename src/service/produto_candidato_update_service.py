from dataclasses import dataclass
from datetime import date
from pathlib import Path

from src.dto.fonte_produto_dto import FonteProdutoDTO
from src.dto.produto_candidato_dto import ProdutoCandidatoDTO
from src.service.fonte_produto_seed_service import FonteProdutoSeedService
from src.service.produto_candidato_catalogo_service import ProdutoCandidatoCatalogoService
from src.service.produto_candidato_scraper_service import ProdutoCandidatoScraperService


@dataclass(frozen=True)
class ProdutoCandidatoUpdateResultado:
    total_fontes: int
    encontrados: list[ProdutoCandidatoDTO]
    produtos_finais: list[ProdutoCandidatoDTO]


class ProdutoCandidatoUpdateService:
    def __init__(
        self,
        scraper_service: ProdutoCandidatoScraperService,
        fonte_service: FonteProdutoSeedService | None = None,
        catalogo_service: ProdutoCandidatoCatalogoService | None = None,
    ) -> None:
        self.scraper_service = scraper_service
        self.fonte_service = fonte_service or FonteProdutoSeedService()
        self.catalogo_service = catalogo_service or ProdutoCandidatoCatalogoService()

    async def atualizar(
        self,
        caminho_fontes: str | Path,
        caminho_saida: str | Path,
        data_referencia: date | None = None,
        limite_por_fonte: int = 10,
        manter_existentes: bool = False,
        salvar: bool = False,
    ) -> ProdutoCandidatoUpdateResultado:
        fontes = self.fonte_service.carregar_de_arquivo(caminho_fontes)
        return await self.atualizar_por_fontes(
            fontes=fontes,
            caminho_saida=caminho_saida,
            data_referencia=data_referencia,
            limite_por_fonte=limite_por_fonte,
            manter_existentes=manter_existentes,
            salvar=salvar,
        )

    async def atualizar_por_fontes(
        self,
        fontes: list[FonteProdutoDTO],
        caminho_saida: str | Path,
        data_referencia: date | None = None,
        limite_por_fonte: int = 10,
        manter_existentes: bool = False,
        salvar: bool = False,
    ) -> ProdutoCandidatoUpdateResultado:
        encontrados = await self.scraper_service.buscar_produtos(
            fontes,
            data_referencia=data_referencia,
            limite_por_fonte=limite_por_fonte,
        )
        produtos_finais = (
            self._combinar_produtos(self.catalogo_service.listar(caminho_saida), encontrados)
            if manter_existentes
            else encontrados
        )

        if salvar:
            self.catalogo_service.salvar(caminho_saida, produtos_finais)

        return ProdutoCandidatoUpdateResultado(
            total_fontes=len(fontes),
            encontrados=encontrados,
            produtos_finais=produtos_finais,
        )

    def _combinar_produtos(
        self,
        existentes: list[ProdutoCandidatoDTO],
        encontrados: list[ProdutoCandidatoDTO],
    ) -> list[ProdutoCandidatoDTO]:
        produtos_por_chave = {
            self.catalogo_service.chave_produto(produto): produto for produto in existentes
        }
        for produto in encontrados:
            produtos_por_chave[self.catalogo_service.chave_produto(produto)] = produto
        return list(produtos_por_chave.values())
