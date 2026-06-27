from src.dto.oferta_dto import OfertaDTO
from src.dto.telegram_message_dto import TelegramMessageDTO
from src.external.telegram.telegram_client import TelegramClient
from src.mapper.telegram_message_mapper import mapear_oferta_para_telegram


class PostagemService:
    def __init__(self, telegram_client: TelegramClient) -> None:
        self.telegram_client = telegram_client

    def formatar_mensagem(self, oferta: OfertaDTO) -> TelegramMessageDTO:
        return mapear_oferta_para_telegram(oferta)

    async def publicar(self, oferta: OfertaDTO) -> tuple[TelegramMessageDTO, str | None]:
        mensagem = self.formatar_mensagem(oferta)
        if not mensagem.image_url:
            raise RuntimeError("Oferta sem imagem nao pode ser publicada no Telegram.")

        message_id = await self.telegram_client.enviar_foto_com_legenda(
            str(mensagem.image_url),
            mensagem.caption,
        )
        return mensagem, message_id
