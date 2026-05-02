"""add_fiscal_identity_to_tenant

Revision ID: c1f3a2b9d4e5
Revises: b468aee317a5
Create Date: 2026-05-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c1f3a2b9d4e5"
down_revision: Union[str, None] = "b468aee317a5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("tenants", sa.Column("fiscal_name", sa.String(255), nullable=True))
    op.add_column("tenants", sa.Column("tax_id", sa.String(20), nullable=True))


def downgrade() -> None:
    op.drop_column("tenants", "tax_id")
    op.drop_column("tenants", "fiscal_name")
