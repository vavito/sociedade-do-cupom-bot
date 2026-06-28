from src.dto.oferta_dto import OfertaDTO
from src.service.filtro_oferta_service import FiltroOfertaService
from src.service.score_oferta_service import ScoreOfertaService


class OfertaService:
    def __init__(
        self,
        filtro_service: FiltroOfertaService | None = None,
        score_service: ScoreOfertaService | None = None,
    ) -> None:
        self.filtro_service = filtro_service or FiltroOfertaService()
        self.score_service = score_service or ScoreOfertaService()

    def selecionar_melhores(self, ofertas: list[OfertaDTO], limite: int = 5) -> list[OfertaDTO]:
        elegiveis = self.filtro_service.filtrar(ofertas)
        pontuadas = self.score_service.aplicar_score(elegiveis)
        return sorted(pontuadas, key=lambda oferta: oferta.score, reverse=True)[:limite]
