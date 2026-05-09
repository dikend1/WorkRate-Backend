"""add enhanced fields and new models

Revision ID: def456
Revises: 1249646a6a17
Create Date: 2025-12-11 15:44:23.605160

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'def456'
down_revision: Union[str, Sequence[str], None] = '1249646a6a17'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
