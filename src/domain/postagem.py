from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Postagem:
    oferta_id: int
    telegram_message_id: str | None
    chat_id: str
    publicada_em: datetime
