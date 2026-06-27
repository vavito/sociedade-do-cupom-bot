import logging
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.domain.marketplace import MarketplaceSlug
from src.dto.oferta_dto import OfertaDTO
from src.external.aliexpress.aliexpress_client import AliExpressClient
from src.infrastructure.database.repositories.marketplace_repository import MarketplaceRepository
from src.infrastructure.database.repositories.oferta_repository import OfertaRepository
from src.infrastructure.database.repositories.pipeline_run_repository import PipelineRunRepository
from src.infrastructure.database.repositories.postagem_repository import PostagemRepository
from src.infrastructure.database.repositories.produto_repository import ProdutoRepository
from src.mapper.aliexpress_offer_mapper import mapear_resposta_aliexpress
from src.service.afiliado_service import AfiliadoService
from src.service.oferta_service import OfertaService
from src.service.postagem_service import PostagemService

logger = logging.getLogger(__name__)

BUSCAS_INICIAIS = [
    "ssd nvme",
    "memoria ram",
    "placa de video",
    "teclado mecanico",
    "mouse gamer",
    "headset gamer",
]


@dataclass(frozen=True)
class PipelineResultado:
    total_encontradas: int
    total_aprovadas: int
    total_postadas: int


class PipelineService:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        aliexpress_client: AliExpressClient,
        oferta_service: OfertaService,
        afiliado_service: AfiliadoService,
        postagem_service: PostagemService,
    ) -> None:
        self.session_factory = session_factory
        self.aliexpress_client = aliexpress_client
        self.oferta_service = oferta_service
        self.afiliado_service = afiliado_service
        self.postagem_service = postagem_service

    async def executar(self) -> PipelineResultado:
        async with self.session_factory() as session:
            run_repository = PipelineRunRepository(session)
            run = await run_repository.iniciar()
            await session.commit()

            total_encontradas = 0
            total_aprovadas = 0
            total_postadas = 0

            try:
                ofertas = await self._buscar_ofertas_aliexpress()
                total_encontradas = len(ofertas)
                selecionadas = self.oferta_service.selecionar_melhores(ofertas)
                total_aprovadas = len(selecionadas)

                for oferta in selecionadas:
                    publicada = await self._publicar_se_nao_duplicada(session, oferta)
                    if publicada:
                        total_postadas += 1

                await run_repository.finalizar(
                    run,
                    status="success",
                    total_encontradas=total_encontradas,
                    total_aprovadas=total_aprovadas,
                    total_postadas=total_postadas,
                )
                await session.commit()
            except Exception as exc:
                await session.rollback()
                logger.exception("Pipeline falhou")
                await run_repository.finalizar(
                    run,
                    status="failed",
                    total_encontradas=total_encontradas,
                    total_aprovadas=total_aprovadas,
                    total_postadas=total_postadas,
                    erro=str(exc),
                )
                await session.commit()
                raise

            return PipelineResultado(
                total_encontradas=total_encontradas,
                total_aprovadas=total_aprovadas,
                total_postadas=total_postadas,
            )

    async def _buscar_ofertas_aliexpress(self) -> list[OfertaDTO]:
        ofertas_por_produto: dict[str, OfertaDTO] = {}

        for keywords in BUSCAS_INICIAIS:
            payload = await self.aliexpress_client.buscar_hot_products(keywords=keywords)
            for oferta in mapear_resposta_aliexpress(payload):
                ofertas_por_produto.setdefault(oferta.produto.external_id, oferta)

        return list(ofertas_por_produto.values())

    async def _publicar_se_nao_duplicada(self, session: AsyncSession, oferta: OfertaDTO) -> bool:
        marketplace_repository = MarketplaceRepository(session)
        produto_repository = ProdutoRepository(session)
        oferta_repository = OfertaRepository(session)
        postagem_repository = PostagemRepository(session)

        marketplace = await marketplace_repository.get_or_create(
            MarketplaceSlug.ALIEXPRESS.value,
            "AliExpress",
        )
        if await oferta_repository.produto_ja_postado(marketplace.id, oferta.produto.external_id):
            logger.info("Produto ja postado, ignorando: %s", oferta.produto.external_id)
            return False

        oferta = await self.afiliado_service.garantir_link_afiliado(oferta)
        if not oferta.produto.imagem_url:
            logger.info("Oferta sem imagem, ignorando: %s", oferta.produto.external_id)
            return False

        produto_model = await produto_repository.get_or_create(marketplace.id, oferta.produto)
        oferta_model = await oferta_repository.salvar(produto_model.id, oferta)
        mensagem, telegram_message_id = await self.postagem_service.publicar(oferta)
        await postagem_repository.salvar(
            oferta_id=oferta_model.id,
            telegram_message_id=telegram_message_id,
            chat_id=self.postagem_service.telegram_client.chat_id,
            caption=mensagem.caption,
        )
        await session.commit()
        return True
