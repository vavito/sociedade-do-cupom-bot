import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.service.pipeline_service import PipelineService

logger = logging.getLogger(__name__)


def criar_scheduler(pipeline_service: PipelineService, interval_minutes: int) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()

    async def executar_pipeline() -> None:
        resultado = await pipeline_service.executar()
        logger.info(
            "Pipeline finalizado: encontradas=%s aprovadas=%s postadas=%s",
            resultado.total_encontradas,
            resultado.total_aprovadas,
            resultado.total_postadas,
        )

    scheduler.add_job(
        executar_pipeline,
        trigger="interval",
        minutes=interval_minutes,
        id="pipeline_ofertas",
        replace_existing=True,
    )
    return scheduler
