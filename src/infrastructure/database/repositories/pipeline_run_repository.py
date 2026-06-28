from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.models import PipelineRunModel


class PipelineRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def iniciar(self) -> PipelineRunModel:
        run = PipelineRunModel(status="running")
        self.session.add(run)
        await self.session.flush()
        return run

    async def finalizar(
        self,
        run: PipelineRunModel,
        status: str,
        total_encontradas: int,
        total_aprovadas: int,
        total_postadas: int,
        erro: str | None = None,
    ) -> None:
        run.status = status
        run.finished_at = datetime.now(UTC)
        run.total_encontradas = total_encontradas
        run.total_aprovadas = total_aprovadas
        run.total_postadas = total_postadas
        run.erro = erro
        await self.session.flush()
