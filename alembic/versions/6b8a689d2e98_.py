"""empty message

Revision ID: 6b8a689d2e98
Revises: 48e00a539c9b
Create Date: 2025-07-20 03:50:19.283050

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '6b8a689d2e98'
down_revision: Union[str, Sequence[str], None] = '48e00a539c9b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('commentmodel', schema=None) as batch_op:
        # <<< LÍNEA CORREGIDA
        batch_op.add_column(sa.Column('rating', sa.Integer(), nullable=False, server_default='3'))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False))

    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('commentmodel', schema=None) as batch_op:
        batch_op.drop_column('updated_at')
        batch_op.drop_column('rating')

    # ### end Alembic commands ###
