"""add docs completion fields

Revision ID: docs_completion_fields
Revises: fix123
Create Date: 2026-05-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'docs_completion_fields'
down_revision: Union[str, Sequence[str], None] = 'fix123'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS facebook_id VARCHAR")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_constraint
                WHERE conname = 'uq_users_facebook_id'
            ) THEN
                ALTER TABLE users
                ADD CONSTRAINT uq_users_facebook_id UNIQUE (facebook_id);
            END IF;
        END
        $$;
        """
    )
    op.execute("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS attachment_url VARCHAR")
    op.execute("ALTER TABLE salaries ADD COLUMN IF NOT EXISTS employment_type VARCHAR")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TABLE salaries DROP COLUMN IF EXISTS employment_type")
    op.execute("ALTER TABLE reviews DROP COLUMN IF EXISTS attachment_url")
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS uq_users_facebook_id")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS facebook_id")
