from pydantic import BaseModel, HttpUrl


class TelegramMessageDTO(BaseModel):
    image_url: HttpUrl | str | None
    caption: str
