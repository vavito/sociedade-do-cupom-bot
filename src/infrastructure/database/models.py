from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class MarketplaceModel(Base):
    __tablename__ = "marketplaces"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    produtos: Mapped[list["ProdutoModel"]] = relationship(back_populates="marketplace")


class ProdutoModel(Base):
    __tablename__ = "produtos"
    __table_args__ = (UniqueConstraint("marketplace_id", "external_id", name="uq_produto_externo"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    marketplace_id: Mapped[int] = mapped_column(ForeignKey("marketplaces.id"), nullable=False)
    external_id: Mapped[str] = mapped_column(String(120), nullable=False)
    titulo: Mapped[str] = mapped_column(Text, nullable=False)
    detalhe_url: Mapped[str] = mapped_column(Text, nullable=False)
    imagem_url: Mapped[str | None] = mapped_column(Text)
    categoria: Mapped[str | None] = mapped_column(String(255))
    marca: Mapped[str | None] = mapped_column(String(255))
    raw_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    marketplace: Mapped[MarketplaceModel] = relationship(back_populates="produtos")
    ofertas: Mapped[list["OfertaModel"]] = relationship(back_populates="produto")


class OfertaModel(Base):
    __tablename__ = "ofertas"

    id: Mapped[int] = mapped_column(primary_key=True)
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id"), nullable=False)
    preco_atual: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    preco_original: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    moeda: Mapped[str] = mapped_column(String(8), nullable=False, default="BRL")
    desconto_percentual: Mapped[int | None] = mapped_column(Integer)
    cupom_codigo: Mapped[str | None] = mapped_column(String(120))
    afiliado_url: Mapped[str] = mapped_column(Text, nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    raw_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    produto: Mapped[ProdutoModel] = relationship(back_populates="ofertas")
    postagem: Mapped["PostagemModel | None"] = relationship(
        back_populates="oferta",
        uselist=False,
    )


class PostagemModel(Base):
    __tablename__ = "postagens"

    id: Mapped[int] = mapped_column(primary_key=True)
    oferta_id: Mapped[int] = mapped_column(ForeignKey("ofertas.id"), unique=True, nullable=False)
    telegram_message_id: Mapped[str | None] = mapped_column(String(120))
    chat_id: Mapped[str] = mapped_column(String(120), nullable=False)
    caption: Mapped[str] = mapped_column(Text, nullable=False)
    posted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    oferta: Mapped[OfertaModel] = relationship(back_populates="postagem")


class PipelineRunModel(Base):
    __tablename__ = "pipeline_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="running")
    total_encontradas: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_aprovadas: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_postadas: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    erro: Mapped[str | None] = mapped_column(Text)
