"""Item 4: create stock_movements table

Revision ID: ccc333333333
Revises: bbb222222222
Create Date: 2026-04-04 00:00:03.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "ccc333333333"
down_revision: Union[str, None] = "bbb222222222"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "stock_movements",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("fruit_id", sa.String(length=36), nullable=False),
        sa.Column("tipo", sa.String(length=10), nullable=False),
        sa.Column("quantidade", sa.Integer(), nullable=False),
        sa.Column("motivo", sa.Text(), nullable=True),
        sa.Column(
            "data_movimento",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["fruit_id"], ["fruits.id"], name="fk_stock_movements_fruit_id"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("quantidade > 0", name="ck_stock_movements_quantidade_positiva"),
        sa.CheckConstraint("tipo IN ('entrada', 'saida')", name="ck_stock_movements_tipo_valido"),
    )
    op.create_index(op.f("ix_stock_movements_fruit_id"), "stock_movements", ["fruit_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_stock_movements_fruit_id"), table_name="stock_movements")
    op.drop_table("stock_movements")
