from typing import cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dto.produto_dto import ProdutoDTO
from src.infrastructure.database.models import ProdutoModel


class ProdutoRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_external_id(
        self,
        marketplace_id: int,
        external_id: str,
    ) -> ProdutoModel | None:
        return cast(
            ProdutoModel | None,
            await self.session.scalar(
                select(ProdutoModel).where(
                    ProdutoModel.marketplace_id == marketplace_id,
                    ProdutoModel.external_id == external_id,
                )
            ),
        )

    async def get_or_create(self, marketplace_id: int, produto: ProdutoDTO) -> ProdutoModel:
        produto_model = await self.get_by_external_id(marketplace_id, produto.external_id)
        if produto_model is not None:
            produto_model.titulo = produto.titulo
            produto_model.detalhe_url = str(produto.detalhe_url)
            produto_model.imagem_url = str(produto.imagem_url) if produto.imagem_url else None
            produto_model.categoria = produto.categoria
            produto_model.marca = produto.marca
            produto_model.raw_data = produto.raw_data
            return produto_model

        produto_model = ProdutoModel(
            marketplace_id=marketplace_id,
            external_id=produto.external_id,
            titulo=produto.titulo,
            detalhe_url=str(produto.detalhe_url),
            imagem_url=str(produto.imagem_url) if produto.imagem_url else None,
            categoria=produto.categoria,
            marca=produto.marca,
            raw_data=produto.raw_data,
        )
        self.session.add(produto_model)
        await self.session.flush()
        return produto_model
