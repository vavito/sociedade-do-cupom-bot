from typing import Any

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

    async def enviar_foto_com_legenda(self, image_url: str, caption: str) -> str | None:
        if not self.bot_token or not self.chat_id:
            raise RuntimeError("TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID precisam estar configurados.")

        url = f"https://api.telegram.org/bot{self.bot_token}/sendPhoto"
        payload = {"chat_id": self.chat_id, "photo": image_url, "caption": caption}

        if self.http_client is not None:
            response = await self.http_client.post(url, data=payload)
        else:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(url, data=payload)

        response.raise_for_status()
        result: dict[str, Any] = response.json().get("result", {})
        message_id = result.get("message_id")
        return str(message_id) if message_id is not None else None
