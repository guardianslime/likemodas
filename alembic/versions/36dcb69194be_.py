"""add requester username to employment request

Revision ID: 36dcb69194be 
Revises: d948151715e5
Create Date: 2025-10-06 20:33:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '36dcb69194be'
down_revision: Union[str, Sequence[str], None] = 'd948151715e5' # Asegúrate que este sea el ID de la revisión anterior
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### Paso 1: Añadir la columna como nullable=True temporalmente ###
    with op.batch_alter_table('employmentrequest', schema=None) as batch_op:
        batch_op.add_column(sa.Column('requester_username', sa.VARCHAR(), nullable=True))

    # ### Paso 2: Rellenar las filas existentes con un valor por defecto ###
    op.execute("UPDATE employmentrequest SET requester_username = 'Solicitud Antigua' WHERE requester_username IS NULL")

    # ### Paso 3: Alterar la columna para que sea NOT NULL como se requiere ###
    with op.batch_alter_table('employmentrequest', schema=None) as batch_op:
        batch_op.alter_column('requester_username',
               existing_type=sa.VARCHAR(),
               nullable=False)


def downgrade() -> None:
    # ### Revertir los cambios ###
    with op.batch_alter_table('employmentrequest', schema=None) as batch_op:
        batch_op.drop_column('requester_username')