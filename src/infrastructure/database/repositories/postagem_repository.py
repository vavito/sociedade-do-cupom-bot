from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.models import PostagemModel


class PostagemRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def salvar(
        self,
        oferta_id: int,
        telegram_message_id: str | None,
        chat_id: str,
        caption: str,
    ) -> PostagemModel:
        postagem = PostagemModel(
            oferta_id=oferta_id,
            telegram_message_id=telegram_message_id,
            chat_id=chat_id,
            caption=caption,
        )
        self.session.add(postagem)
        await self.session.flush()
        return postagem
