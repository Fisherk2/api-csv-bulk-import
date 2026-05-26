"""add_customers_table

Revision ID: 20260527_0001
Revises: 53c449c716bb
Create Date: 2026-05-27 00:01:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260527_0001'
down_revision: Union[str, None] = '53c449c716bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'customers',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )
    op.create_index(
        op.f('ix_customers_name'), 'customers', ['name'], unique=False
    )
    op.create_index(
        op.f('ix_customers_email'), 'customers', ['email'], unique=True
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_customers_email'), table_name='customers')
    op.drop_index(op.f('ix_customers_name'), table_name='customers')
    op.drop_table('customers')
