"""Add GIN index for variants vuid

Revision ID: 057ac65d952b
Revises: 00230ab609bb
Create Date: 2025-09-20 10:33:00.672032

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '057ac65d952b'
down_revision: Union[str, Sequence[str], None] = '00230ab609bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    paass
