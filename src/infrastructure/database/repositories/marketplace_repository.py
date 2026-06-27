from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.models import MarketplaceModel


class MarketplaceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_or_create(self, slug: str, nome: str) -> MarketplaceModel:
        marketplace = await self.session.scalar(
            select(MarketplaceModel).where(MarketplaceModel.slug == slug)
        )
        if marketplace is not None:
            return marketplace

        marketplace = MarketplaceModel(slug=slug, nome=nome)
        self.session.add(marketplace)
        await self.session.flush()
        return marketplace
