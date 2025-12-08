"""change currency to varchar nullable

Revision ID: abc123
Revises: f8438ccc2fc4
Create Date: 2025-12-08 22:26:32.243732

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'abc123'
down_revision: Union[str, Sequence[str], None] = 'f8438ccc2fc4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('salaries', 'currency', nullable=True, type_=sa.String())


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('salaries', 'currency', nullable=False, type_=sa.String(3))
