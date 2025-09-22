"""add_gin_index_to_variants

Revision ID: 76966806eea6
Revises: 79f2255bb1eb
Create Date: 2025-09-21 21:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '<EL_NUEVO_ID_QUE_SE_GENERO>' # Reemplaza esto con el ID real del archivo
down_revision: Union[str, Sequence[str], None] = '79f2255bb1eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Crea el índice GIN en la columna 'variants' para búsquedas JSONB eficientes
    op.create_index(
        'ix_blogpostmodel_variants_gin',
        'blogpostmodel',
        ['variants'],
        unique=False,
        postgresql_using='gin'
    )


def downgrade() -> None:
    # Elimina el índice si se revierte la migración
    op.drop_index('ix_blogpostmodel_variants_gin', table_name='blogpostmodel')