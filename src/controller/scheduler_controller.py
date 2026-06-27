import asyncio
import logging

from src.infrastructure.scheduler.scheduler import criar_scheduler
from src.service.pipeline_service import PipelineService

logger = logging.getLogger(__name__)


class SchedulerController:
    def __init__(self, pipeline_service: PipelineService, interval_minutes: int) -> None:
        self.pipeline_service = pipeline_service
        self.interval_minutes = interval_minutes

    async def iniciar(self) -> None:
        resultado = await self.pipeline_service.executar()
        logger.info(
            "Primeira execucao finalizada: encontradas=%s aprovadas=%s postadas=%s",
            resultado.total_encontradas,
            resultado.total_aprovadas,
            resultado.total_postadas,
        )

        scheduler = criar_scheduler(self.pipeline_service, self.interval_minutes)
        scheduler.start()
        try:
            while True:
                await asyncio.sleep(3600)
        finally:
            scheduler.shutdown()
