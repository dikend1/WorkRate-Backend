"""add_enhanced_fields_and_new_models

Revision ID: 1249646a6a17
Revises: fa9430914c71
Create Date: 2025-12-11 15:39:39.942950

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1249646a6a17'
down_revision: Union[str, Sequence[str], None] = 'fa9430914c71'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
