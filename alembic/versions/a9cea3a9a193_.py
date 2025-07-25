"""empty message

Revision ID: a9cea3a9a193
Revises: 5b8f71e35981
Create Date: 2025-07-22 18:08:19.568356

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = 'a9cea3a9a193'
down_revision: Union[str, Sequence[str], None] = '5b8f71e35981'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('blogpostmodel', schema=None) as batch_op:
        batch_op.add_column(sa.Column('category', sa.String(), server_default='otros', nullable=False))

    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('blogpostmodel', schema=None) as batch_op:
        batch_op.drop_column('category')

    # ### end Alembic commands ###
