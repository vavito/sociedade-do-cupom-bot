import asyncio

from src.config.settings import get_settings
from src.controller.scheduler_controller import SchedulerController
from src.external.aliexpress.aliexpress_client import AliExpressClient
from src.external.telegram.telegram_client import TelegramClient
from src.infrastructure.database.session import criar_session_factory
from src.infrastructure.logger.logger import configure_logging
from src.service.afiliado_service import AfiliadoService
from src.service.oferta_service import OfertaService
from src.service.pipeline_service import PipelineService
from src.service.postagem_service import PostagemService


async def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)

    session_factory = criar_session_factory(settings)
    aliexpress_client = AliExpressClient(
        app_key=settings.aliexpress_app_key,
        app_secret=settings.aliexpress_app_secret,
        tracking_id=settings.aliexpress_tracking_id,
        base_url=settings.aliexpress_api_base_url,
    )
    telegram_client = TelegramClient(
        bot_token=settings.telegram_bot_token,
        chat_id=settings.telegram_chat_id,
    )
    afiliado_service = AfiliadoService(aliexpress_client)
    pipeline_service = PipelineService(
        session_factory=session_factory,
        aliexpress_client=aliexpress_client,
        oferta_service=OfertaService(),
        afiliado_service=afiliado_service,
        postagem_service=PostagemService(telegram_client),
    )
    controller = SchedulerController(
        pipeline_service=pipeline_service,
        interval_minutes=settings.scheduler_interval_minutes,
    )
    await controller.iniciar()


if __name__ == "__main__":
    asyncio.run(main())
