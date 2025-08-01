"""Add is_verified column to UserInfo

Revision ID: 8f8f34d331bc
Revises: 9dc3ee0a1da2
Create Date: 2025-07-18 21:28:59.285943

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8f8f34d331bc'
down_revision: Union[str, Sequence[str], None] = '9dc3ee0a1da2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('verificationtoken',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('token', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('userinfo_id', sa.Integer(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['userinfo_id'], ['userinfo.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_verificationtoken_token'), 'verificationtoken', ['token'], unique=True)

    op.add_column('userinfo', sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'))

    # Los siguientes son ajustes menores de tipo de dato detectados por Alembic.
    op.alter_column('blogpostmodel', 'publish_date',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.DateTime(),
               existing_nullable=False)
    op.alter_column('blogpostmodel', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.DateTime(),
               existing_nullable=False,
               existing_server_default=sa.text('now()'))
    op.alter_column('blogpostmodel', 'updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.DateTime(),
               existing_nullable=False,
               existing_server_default=sa.text('now()'))
    op.alter_column('notificationmodel', 'message',
               existing_type=sa.TEXT(),
               type_=sqlmodel.sql.sqltypes.AutoString(),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('notificationmodel', 'message',
               existing_type=sqlmodel.sql.sqltypes.AutoString(),
               type_=sa.TEXT(),
               existing_nullable=False)
    op.alter_column('blogpostmodel', 'updated_at',
               existing_type=sa.DateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=False,
               existing_server_default=sa.text('now()'))
    op.alter_column('blogpostmodel', 'created_at',
               existing_type=sa.DateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=False,
               existing_server_default=sa.text('now()'))
    op.alter_column('blogpostmodel', 'publish_date',
               existing_type=sa.DateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=False)

    op.drop_column('userinfo', 'is_verified')

    op.drop_index(op.f('ix_verificationtoken_token'), table_name='verificationtoken')
    op.drop_table('verificationtoken')
    # ### end Alembic commands ###