# alembic/versions/873b2cfc32a0_add_2fa_fields_to_userinfo.py (CORREGIDO)

"""add_2fa_fields_to_userinfo

Revision ID: 873b2cfc32a0
Revises: 48edf551e18e
Create Date: 2025-10-02 00:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel  # <- Se añade la importación que faltaba

# revision identifiers, used by Alembic.
revision: str = '873b2cfc32a0'
down_revision: Union[str, Sequence[str], None] = '48edf551e18e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Añade los campos tfa_secret y tfa_enabled a la tabla userinfo."""
    with op.batch_alter_table('userinfo', schema=None) as batch_op:
        # Se usa sa.String() que es más estándar y ya está importado
        batch_op.add_column(sa.Column('tfa_secret', sa.String(), nullable=True))
        # Se usa sa.Boolean() y se establece el valor por defecto directamente
        batch_op.add_column(sa.Column('tfa_enabled', sa.Boolean(), server_default=sa.false(), nullable=False))


def downgrade() -> None:
    """Revierte la adición de los campos de 2FA."""
    with op.batch_alter_table('userinfo', schema=None) as batch_op:
        batch_op.drop_column('tfa_enabled')
        batch_op.drop_column('tfa_secret')