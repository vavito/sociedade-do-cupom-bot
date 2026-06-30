import pytest

from src.dto.telegram_message_dto import TelegramMessageDTO
from src.service.cupom_postagem_service import CupomPostagemService


class FakeTelegramClient:
    def __init__(self) -> None:
        self.enviadas: list[tuple[str, str]] = []

    async def enviar_foto_com_legenda(self, image_url: str, caption: str) -> str:
        self.enviadas.append((image_url, caption))
        return f"msg-{len(self.enviadas)}"


async def test_publica_mensagem_de_cupom_com_foto() -> None:
    telegram_client = FakeTelegramClient()
    service = CupomPostagemService(telegram_client)  # type: ignore[arg-type]
    mensagem = TelegramMessageDTO(image_url="https://example.com/banner.jpg", caption="Cupom")

    resultado = await service.publicar(mensagem)

    assert resultado.telegram_message_id == "msg-1"
    assert resultado.mensagem == mensagem
    assert telegram_client.enviadas == [("https://example.com/banner.jpg", "Cupom")]


async def test_publica_lote_de_mensagens_de_cupom() -> None:
    telegram_client = FakeTelegramClient()
    service = CupomPostagemService(telegram_client)  # type: ignore[arg-type]

    resultados = await service.publicar_lote(
        [
            TelegramMessageDTO(image_url="https://example.com/1.jpg", caption="Cupom 1"),
            TelegramMessageDTO(image_url="https://example.com/2.jpg", caption="Cupom 2"),
        ]
    )

    assert [resultado.telegram_message_id for resultado in resultados] == ["msg-1", "msg-2"]
    assert telegram_client.enviadas == [
        ("https://example.com/1.jpg", "Cupom 1"),
        ("https://example.com/2.jpg", "Cupom 2"),
    ]


async def test_rejeita_post_de_cupom_sem_imagem() -> None:
    service = CupomPostagemService(FakeTelegramClient())  # type: ignore[arg-type]
    mensagem = TelegramMessageDTO(image_url=None, caption="Cupom")

    with pytest.raises(RuntimeError, match="sem imagem"):
        await service.publicar(mensagem)


async def test_rejeita_legenda_maior_que_limite_do_telegram() -> None:
    service = CupomPostagemService(FakeTelegramClient())  # type: ignore[arg-type]
    mensagem = TelegramMessageDTO(
        image_url="https://example.com/banner.jpg",
        caption="x" * 1025,
    )

    with pytest.raises(RuntimeError, match="maior que o limite"):
        await service.publicar(mensagem)
