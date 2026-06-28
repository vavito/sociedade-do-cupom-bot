from src.dto.oferta_dto import OfertaDTO
from src.dto.telegram_message_dto import TelegramMessageDTO
from src.external.telegram.telegram_client import TelegramClient
from src.mapper.telegram_message_mapper import mapear_oferta_para_telegram


class PostagemService:
    TELEGRAM_PHOTO_CAPTION_LIMIT = 1024

    def __init__(self, telegram_client: TelegramClient) -> None:
        self.telegram_client = telegram_client

    def formatar_mensagem(self, oferta: OfertaDTO) -> TelegramMessageDTO:
        return mapear_oferta_para_telegram(oferta)

    async def publicar(self, oferta: OfertaDTO) -> tuple[TelegramMessageDTO, str | None]:
        mensagem = self.formatar_mensagem(oferta)
        if not mensagem.image_url:
            raise RuntimeError("Oferta sem imagem nao pode ser publicada no Telegram.")

        if len(mensagem.caption) > self.TELEGRAM_PHOTO_CAPTION_LIMIT:
            await self.telegram_client.enviar_foto_com_legenda(
                str(mensagem.image_url),
                self._criar_caption_curta(oferta),
            )
            message_id = await self.telegram_client.enviar_mensagem(mensagem.caption)
            return mensagem, message_id

        message_id = await self.telegram_client.enviar_foto_com_legenda(
            str(mensagem.image_url),
            mensagem.caption,
        )
        return mensagem, message_id

    def _criar_caption_curta(self, oferta: OfertaDTO) -> str:
        linhas = [
            f"🔥 {oferta.produto.titulo}",
            "",
            "Link no próximo post.",
            "",
            "(Anuncio)",
        ]
        caption = "\n".join(linhas)
        if len(caption) <= self.TELEGRAM_PHOTO_CAPTION_LIMIT:
            return caption
        return f"🔥 {oferta.produto.titulo[:900]}\n\nLink no próximo post.\n\n(Anuncio)"
