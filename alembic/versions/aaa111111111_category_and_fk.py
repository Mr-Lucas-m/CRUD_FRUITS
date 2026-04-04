"""Item 2: create categories table and add category_id FK to fruits

Revision ID: aaa111111111
Revises: 79dee2c61eb6
Create Date: 2026-04-04 00:00:01.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "aaa111111111"
down_revision: Union[str, None] = "79dee2c61eb6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("nome", sa.String(length=80), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column(
            "data_cadastro",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_categories_nome"), "categories", ["nome"], unique=True)

    op.add_column("fruits", sa.Column("category_id", sa.String(length=36), nullable=True))
    op.create_foreign_key(
        "fk_fruits_category_id",
        "fruits",
        "categories",
        ["category_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_fruits_category_id", "fruits", type_="foreignkey")
    op.drop_column("fruits", "category_id")
    op.drop_index(op.f("ix_categories_nome"), table_name="categories")
    op.drop_table("categories")
