import asyncio
import logging
from dataclasses import dataclass

from src.dto.oferta_dto import OfertaDTO
from src.external.telegram.telegram_client import TelegramClient
from src.service.gerador_post_service import GeradorPostService
from src.service.postagem_service import PostagemService

logger = logging.getLogger(__name__)

MENU = "Escolha uma opcao:\n1. Gerar post\n2. Sair"
PEDIR_LINK = "Envie um link valido da AliExpress ou Shopee."
MENU_POST_GERADO = "1. Postar no canal\n2. Gerar novo post\n3. Sair"


@dataclass
class ConversaState:
    etapa: str = "menu"
    oferta: OfertaDTO | None = None


class TelegramPostController:
    def __init__(
        self,
        telegram_client: TelegramClient,
        gerador_post_service: GeradorPostService,
        postagem_service: PostagemService,
    ) -> None:
        self.telegram_client = telegram_client
        self.gerador_post_service = gerador_post_service
        self.postagem_service = postagem_service
        self._states: dict[str, ConversaState] = {}
        self._offset: int | None = None

    async def iniciar(self) -> None:
        logger.info("Telegram post bot iniciado")
        while True:
            try:
                updates = await self.telegram_client.get_updates(offset=self._offset)
                for update in updates:
                    self._offset = int(update["update_id"]) + 1
                    await self._processar_update(update)
            except Exception:
                logger.exception("Erro ao processar updates do Telegram")
                await asyncio.sleep(5)

    async def _processar_update(self, update: dict) -> None:
        message = update.get("message")
        if not isinstance(message, dict):
            return

        chat = message.get("chat", {})
        chat_id = str(chat.get("id", ""))
        texto = str(message.get("text") or "").strip()
        if not chat_id or not texto:
            return

        state = self._states.setdefault(chat_id, ConversaState())
        if texto.lower() in {"/start", "menu"}:
            state.etapa = "menu"
            state.oferta = None
            await self.telegram_client.enviar_mensagem(MENU, chat_id=chat_id)
            return

        if state.etapa == "aguardando_link":
            await self._gerar_post(chat_id, texto, state)
            return

        if state.etapa == "post_gerado":
            await self._processar_post_gerado(chat_id, texto, state)
            return

        await self._processar_menu(chat_id, texto, state)

    async def _processar_menu(self, chat_id: str, texto: str, state: ConversaState) -> None:
        if texto == "1":
            state.etapa = "aguardando_link"
            state.oferta = None
            await self.telegram_client.enviar_mensagem(PEDIR_LINK, chat_id=chat_id)
            return

        if texto == "2":
            self._states.pop(chat_id, None)
            await self.telegram_client.enviar_mensagem("Fluxo encerrado.", chat_id=chat_id)
            return

        await self.telegram_client.enviar_mensagem(MENU, chat_id=chat_id)

    async def _gerar_post(self, chat_id: str, link: str, state: ConversaState) -> None:
        try:
            oferta, mensagem = await self.gerador_post_service.gerar_por_link(link)
        except Exception as exc:
            logger.info("Nao foi possivel gerar post: %s", exc)
            self._states.pop(chat_id, None)
            await self.telegram_client.enviar_mensagem(
                "Nao consegui gerar o post para esse link. Fluxo encerrado.",
                chat_id=chat_id,
            )
            return

        state.etapa = "post_gerado"
        state.oferta = oferta
        await self.telegram_client.enviar_mensagem(mensagem.caption, chat_id=chat_id)
        await self.telegram_client.enviar_mensagem(MENU_POST_GERADO, chat_id=chat_id)

    async def _processar_post_gerado(
        self,
        chat_id: str,
        texto: str,
        state: ConversaState,
    ) -> None:
        if texto == "1" and state.oferta is not None:
            await self.postagem_service.publicar(state.oferta)
            self._states.pop(chat_id, None)
            await self.telegram_client.enviar_mensagem(
                "Post publicado no canal.\n\n1. Gerar post\n2. Sair",
                chat_id=chat_id,
            )
            return

        if texto == "2":
            state.etapa = "aguardando_link"
            state.oferta = None
            await self.telegram_client.enviar_mensagem(PEDIR_LINK, chat_id=chat_id)
            return

        if texto == "3":
            self._states.pop(chat_id, None)
            await self.telegram_client.enviar_mensagem("Fluxo encerrado.", chat_id=chat_id)
            return

        await self.telegram_client.enviar_mensagem(MENU_POST_GERADO, chat_id=chat_id)
