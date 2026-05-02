"""add needs_review to financial_entry

Revision ID: e3f7b1c9d2a4
Revises: 94b32853dd7e
Create Date: 2026-05-02 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e3f7b1c9d2a4'
down_revision: Union[str, Sequence[str], None] = '94b32853dd7e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'financial_entries',
        sa.Column('needs_review', sa.Boolean(), nullable=False, server_default='false'),
    )
    op.create_index('ix_financial_entries_needs_review', 'financial_entries', ['needs_review'])


def downgrade() -> None:
    op.drop_index('ix_financial_entries_needs_review', table_name='financial_entries')
    op.drop_column('financial_entries', 'needs_review')
