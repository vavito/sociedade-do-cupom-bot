from pathlib import Path
from typing import Any

import httpx

from src.external.telegram.telegram_client import TelegramClient


class FakeHTTPClient:
    def __init__(self) -> None:
        self.data: dict[str, Any] | None = None
        self.files: dict[str, Any] | None = None
        self.file_name: str | None = None
        self.file_content: bytes | None = None

    async def post(
        self,
        url: str,
        data: dict[str, Any],
        files: dict[str, Any] | None = None,
    ) -> httpx.Response:
        self.data = data
        self.files = files

        if files:
            file_name, file_obj = files["photo"]
            self.file_name = file_name
            self.file_content = file_obj.read()

        return httpx.Response(200, json={"ok": True, "result": {"message_id": 123}})


async def test_envia_url_publica_como_photo() -> None:
    http_client = FakeHTTPClient()
    client = TelegramClient("token", "chat", http_client=http_client)  # type: ignore[arg-type]

    message_id = await client.enviar_foto_com_legenda("https://example.com/banner.jpg", "texto")

    assert message_id == "123"
    assert http_client.data == {
        "chat_id": "chat",
        "photo": "https://example.com/banner.jpg",
        "caption": "texto",
    }
    assert http_client.files is None


async def test_envia_arquivo_local_como_upload(tmp_path: Path) -> None:
    image_path = tmp_path / "banner.jpg"
    image_path.write_bytes(b"imagem")
    http_client = FakeHTTPClient()
    client = TelegramClient("token", "chat", http_client=http_client)  # type: ignore[arg-type]

    message_id = await client.enviar_foto_com_legenda(str(image_path), "texto")

    assert message_id == "123"
    assert http_client.data == {"chat_id": "chat", "caption": "texto"}
    assert http_client.file_name == "banner.jpg"
    assert http_client.file_content == b"imagem"
