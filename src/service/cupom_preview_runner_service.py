from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from src.dto.cupom_produto_match_dto import CupomProdutoMatchDTO
from src.dto.telegram_message_dto import TelegramMessageDTO
from src.service.cupom_produto_preview_pipeline_service import (
    CupomProdutoPreviewPipelineService,
)
from src.service.cupom_scraper_service import CupomScraperService
from src.service.produto_candidato_seed_service import ProdutoCandidatoSeedService


@dataclass(frozen=True)
class CupomPreviewRunnerResultado:
    total_cupons: int
    total_produtos: int
    previews: list[tuple[CupomProdutoMatchDTO, TelegramMessageDTO]]

    @property
    def total_previews(self) -> int:
        return len(self.previews)


class CupomPreviewRunnerService:
    def __init__(
        self,
        scraper_service: CupomScraperService,
        seed_service: ProdutoCandidatoSeedService | None = None,
        preview_pipeline: CupomProdutoPreviewPipelineService | None = None,
    ) -> None:
        self.scraper_service = scraper_service
        self.seed_service = seed_service or ProdutoCandidatoSeedService()
        self.preview_pipeline = preview_pipeline or CupomProdutoPreviewPipelineService()

    async def gerar_previews(
        self,
        caminho_produtos: str | Path,
        data_referencia: date | None = None,
        postagens_por_produto: dict[str, list[datetime]] | None = None,
        agora: datetime | None = None,
        limite: int = 10,
        filtrar_cupons: bool = True,
    ) -> CupomPreviewRunnerResultado:
        momento = agora or datetime.now()
        data_produtos = data_referencia or momento.date()
        cupons = await self.scraper_service.buscar_cupons_iniciais(filtrar=filtrar_cupons)
        produtos = self.seed_service.carregar_de_arquivo(caminho_produtos, data_produtos)
        previews = self.preview_pipeline.gerar_previews(
            cupons=cupons,
            produtos=produtos,
            postagens_por_produto=postagens_por_produto or {},
            agora=momento,
            limite=limite,
        )

        return CupomPreviewRunnerResultado(
            total_cupons=len(cupons),
            total_produtos=len(produtos),
            previews=previews,
        )
