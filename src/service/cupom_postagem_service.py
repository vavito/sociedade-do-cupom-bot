from dataclasses import dataclass

from src.dto.telegram_message_dto import TelegramMessageDTO
from src.external.telegram.telegram_client import TelegramClient


@dataclass(frozen=True)
class CupomPostagemResultado:
    mensagem: TelegramMessageDTO
    telegram_message_id: str | None


class CupomPostagemService:
    TELEGRAM_PHOTO_CAPTION_LIMIT = 1024

    def __init__(self, telegram_client: TelegramClient) -> None:
        self.telegram_client = telegram_client

    async def publicar(self, mensagem: TelegramMessageDTO) -> CupomPostagemResultado:
        if not mensagem.image_url:
            raise RuntimeError("Post de cupom sem imagem nao pode ser publicado no Telegram.")

        if len(mensagem.caption) > self.TELEGRAM_PHOTO_CAPTION_LIMIT:
            raise RuntimeError("Legenda de cupom maior que o limite do Telegram.")

        telegram_message_id = await self.telegram_client.enviar_foto_com_legenda(
            str(mensagem.image_url),
            mensagem.caption,
        )
        return CupomPostagemResultado(
            mensagem=mensagem,
            telegram_message_id=telegram_message_id,
        )

    async def publicar_lote(
        self,
        mensagens: list[TelegramMessageDTO],
    ) -> list[CupomPostagemResultado]:
        resultados = []
        for mensagem in mensagens:
            resultados.append(await self.publicar(mensagem))
        return resultados
