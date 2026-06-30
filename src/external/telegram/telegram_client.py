from pathlib import Path
from typing import Any, cast
from urllib.parse import urlparse

import httpx


class TelegramClient:
    def __init__(
        self,
        bot_token: str,
        chat_id: str,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.http_client = http_client

    async def enviar_foto_com_legenda(
        self,
        image_url: str,
        caption: str,
        chat_id: str | None = None,
    ) -> str | None:
        target_chat_id = self._resolver_chat_id(chat_id)

        payload = {"chat_id": target_chat_id, "caption": caption}
        local_path = self._resolver_arquivo_local(image_url)
        if local_path:
            with local_path.open("rb") as image_file:
                result = await self._post(
                    "sendPhoto",
                    payload,
                    files={"photo": (local_path.name, image_file)},
                )
        else:
            payload["photo"] = image_url
            result = await self._post("sendPhoto", payload)

        message_id = result.get("message_id")
        return str(message_id) if message_id is not None else None

    async def enviar_mensagem(self, text: str, chat_id: str | None = None) -> str | None:
        target_chat_id = self._resolver_chat_id(chat_id)

        payload = {"chat_id": target_chat_id, "text": text, "disable_web_page_preview": False}
        result = await self._post("sendMessage", payload)
        message_id = result.get("message_id")
        return str(message_id) if message_id is not None else None

    async def get_updates(
        self, offset: int | None = None, timeout: int = 30
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"timeout": timeout}
        if offset is not None:
            params["offset"] = offset

        result = await self._post("getUpdates", params)
        if isinstance(result, list):
            return [update for update in result if isinstance(update, dict)]
        return []

    async def _post(
        self,
        method: str,
        payload: dict[str, Any],
        files: dict[str, Any] | None = None,
    ) -> Any:
        if not self.bot_token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN precisa estar configurado.")

        url = f"https://api.telegram.org/bot{self.bot_token}/{method}"
        if self.http_client is not None:
            response = await self.http_client.post(url, data=payload, files=files)
        else:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(url, data=payload, files=files)

        payload = cast(dict[str, Any], response.json())
        if response.status_code >= 400 or not payload.get("ok", False):
            description = payload.get("description", "erro desconhecido")
            raise RuntimeError(f"Erro Telegram: {response.status_code} - {description}")

        return payload.get("result", {})

    @staticmethod
    def _resolver_arquivo_local(image_url: str) -> Path | None:
        scheme = urlparse(image_url).scheme
        if scheme in {"http", "https"}:
            return None

        path = Path(image_url)
        return path if path.is_file() else None

    def _resolver_chat_id(self, chat_id: str | None) -> str:
        target_chat_id = chat_id or self.chat_id
        if not target_chat_id:
            raise RuntimeError("TELEGRAM_CHAT_ID precisa estar configurado.")
        return target_chat_id
