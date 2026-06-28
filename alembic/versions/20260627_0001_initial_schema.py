"""initial schema

Revision ID: 20260627_0001
Revises:
Create Date: 2026-06-27
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260627_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "marketplaces",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=60), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("slug"),
    )
    op.create_table(
        "pipeline_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("total_encontradas", sa.Integer(), nullable=False),
        sa.Column("total_aprovadas", sa.Integer(), nullable=False),
        sa.Column("total_postadas", sa.Integer(), nullable=False),
        sa.Column("erro", sa.Text(), nullable=True),
    )
    op.create_table(
        "produtos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("marketplace_id", sa.Integer(), nullable=False),
        sa.Column("external_id", sa.String(length=120), nullable=False),
        sa.Column("titulo", sa.Text(), nullable=False),
        sa.Column("detalhe_url", sa.Text(), nullable=False),
        sa.Column("imagem_url", sa.Text(), nullable=True),
        sa.Column("categoria", sa.String(length=255), nullable=True),
        sa.Column("marca", sa.String(length=255), nullable=True),
        sa.Column("raw_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["marketplace_id"], ["marketplaces.id"]),
        sa.UniqueConstraint("marketplace_id", "external_id", name="uq_produto_externo"),
    )
    op.create_table(
        "ofertas",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("produto_id", sa.Integer(), nullable=False),
        sa.Column("preco_atual", sa.Numeric(12, 2), nullable=False),
        sa.Column("preco_original", sa.Numeric(12, 2), nullable=True),
        sa.Column("moeda", sa.String(length=8), nullable=False),
        sa.Column("desconto_percentual", sa.Integer(), nullable=True),
        sa.Column("cupom_codigo", sa.String(length=120), nullable=True),
        sa.Column("afiliado_url", sa.Text(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("raw_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["produto_id"], ["produtos.id"]),
    )
    op.create_table(
        "postagens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("oferta_id", sa.Integer(), nullable=False),
        sa.Column("telegram_message_id", sa.String(length=120), nullable=True),
        sa.Column("chat_id", sa.String(length=120), nullable=False),
        sa.Column("caption", sa.Text(), nullable=False),
        sa.Column(
            "posted_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["oferta_id"], ["ofertas.id"]),
        sa.UniqueConstraint("oferta_id"),
    )


def downgrade() -> None:
    op.drop_table("postagens")
    op.drop_table("ofertas")
    op.drop_table("produtos")
    op.drop_table("pipeline_runs")
    op.drop_table("marketplaces")
