"""create fruits table

Revision ID: 79dee2c61eb6
Revises: 
Create Date: 2026-04-03 12:15:58.670717

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '79dee2c61eb6'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'fruits',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('preco', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('quantidade_estoque', sa.Integer(), nullable=False),
        sa.Column('data_cadastro', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('data_atualizacao', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('preco > 0', name='ck_fruits_preco_positivo'),
        sa.CheckConstraint('quantidade_estoque >= 0', name='ck_fruits_estoque_nao_negativo'),
    )
    op.create_index(op.f('ix_fruits_nome'), 'fruits', ['nome'], unique=True)
    op.create_index(op.f('ix_fruits_data_cadastro'), 'fruits', ['data_cadastro'])


def downgrade() -> None:
    op.drop_index(op.f('ix_fruits_data_cadastro'), table_name='fruits')
    op.drop_index(op.f('ix_fruits_nome'), table_name='fruits')
    op.drop_table('fruits')
