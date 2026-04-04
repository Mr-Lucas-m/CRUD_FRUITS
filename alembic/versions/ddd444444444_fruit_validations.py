"""Item 5: add unidade_medida, estoque_minimo, preco_custo to fruits

Revision ID: ddd444444444
Revises: ccc333333333
Create Date: 2026-04-04 00:00:04.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "ddd444444444"
down_revision: Union[str, None] = "ccc333333333"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "fruits",
        sa.Column(
            "unidade_medida",
            sa.String(length=20),
            nullable=False,
            server_default="unidade",
        ),
    )
    op.add_column(
        "fruits",
        sa.Column("estoque_minimo", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "fruits",
        sa.Column("preco_custo", sa.Numeric(precision=10, scale=2), nullable=True),
    )
    op.create_check_constraint(
        "ck_fruits_unidade_medida_valida",
        "fruits",
        "unidade_medida IN ('kg', 'unidade', 'caixa', 'duzia')",
    )
    op.create_check_constraint(
        "ck_fruits_estoque_minimo_nao_negativo",
        "fruits",
        "estoque_minimo >= 0",
    )


def downgrade() -> None:
    op.drop_constraint("ck_fruits_estoque_minimo_nao_negativo", "fruits", type_="check")
    op.drop_constraint("ck_fruits_unidade_medida_valida", "fruits", type_="check")
    op.drop_column("fruits", "preco_custo")
    op.drop_column("fruits", "estoque_minimo")
    op.drop_column("fruits", "unidade_medida")
