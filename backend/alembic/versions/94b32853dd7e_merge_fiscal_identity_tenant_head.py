"""merge fiscal identity tenant head

Revision ID: 94b32853dd7e
Revises: a1be718514ec, c1f3a2b9d4e5
Create Date: 2026-05-01 20:35:51.140389

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '94b32853dd7e'
down_revision: Union[str, Sequence[str], None] = ('a1be718514ec', 'c1f3a2b9d4e5')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
