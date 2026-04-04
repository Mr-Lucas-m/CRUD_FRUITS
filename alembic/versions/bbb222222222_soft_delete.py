"""Item 3: add deleted_at to fruits (soft delete)

Revision ID: bbb222222222
Revises: aaa111111111
Create Date: 2026-04-04 00:00:02.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "bbb222222222"
down_revision: Union[str, None] = "aaa111111111"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "fruits",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_fruits_deleted_at", "fruits", ["deleted_at"])


def downgrade() -> None:
    op.drop_index("ix_fruits_deleted_at", table_name="fruits")
    op.drop_column("fruits", "deleted_at")
