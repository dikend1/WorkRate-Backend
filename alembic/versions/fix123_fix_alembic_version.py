"""fix alembic version

Revision ID: fix123
Revises: def456
Create Date: 2025-12-11 15:45:23.174423

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fix123'
down_revision: Union[str, Sequence[str], None] = 'def456'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
