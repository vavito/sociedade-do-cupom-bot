from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dto.oferta_dto import OfertaDTO
from src.infrastructure.database.models import OfertaModel, PostagemModel, ProdutoModel


class OfertaRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def produto_ja_postado(self, marketplace_id: int, external_id: str) -> bool:
        statement = select(
            exists()
            .where(ProdutoModel.marketplace_id == marketplace_id)
            .where(ProdutoModel.external_id == external_id)
            .where(OfertaModel.produto_id == ProdutoModel.id)
            .where(PostagemModel.oferta_id == OfertaModel.id)
        )
        return bool(await self.session.scalar(statement))

    async def salvar(self, produto_id: int, oferta: OfertaDTO) -> OfertaModel:
        oferta_model = OfertaModel(
            produto_id=produto_id,
            preco_atual=oferta.preco_atual,
            preco_original=oferta.preco_original,
            moeda=oferta.moeda,
            desconto_percentual=oferta.desconto_percentual,
            cupom_codigo=oferta.cupom_codigo,
            afiliado_url=str(oferta.afiliado_url),
            score=oferta.score,
            raw_data=oferta.raw_data,
        )
        self.session.add(oferta_model)
        await self.session.flush()
        return oferta_model
