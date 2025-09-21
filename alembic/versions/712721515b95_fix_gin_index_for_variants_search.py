"""fix_gin_index_for_variants_search

Revision ID: 712721515b95
Revises: 057ac65d952b
Create Date: 2025-09-21 14:49:46.779120

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '712721515b95'
down_revision: Union[str, Sequence[str], None] = '057ac65d952b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Elimina el índice GIN incorrecto y crea uno nuevo y optimizado sobre
    toda la columna 'variants' para acelerar las búsquedas de VUID.
    """
    # Intentamos eliminar el índice antiguo. Si no existe, no hay problema.
    try:
        op.drop_index('ix_blogpostmodel_variants_vuid', table_name='blogpostmodel')
    except Exception as e:
        print(f"INFO: No se pudo eliminar el índice 'ix_blogpostmodel_variants_vuid', puede que no exista. Error: {e}")

    # Creamos el nuevo índice GIN correcto, que indexa todo el contenido de la columna 'variants'.
    op.create_index(
        'ix_blogpostmodel_variants',
        'blogpostmodel',
        ['variants'],
        unique=False,
        postgresql_using='gin'
    )


def downgrade() -> None:
    """
    Revierte los cambios: elimina el nuevo índice GIN y recrea el
    antiguo e incorrecto, para mantener la reversibilidad.
    """
    # Elimina el nuevo índice que creamos en upgrade()
    op.drop_index('ix_blogpostmodel_variants', table_name='blogpostmodel')

    # Recrea el índice antiguo que existía antes
    op.execute("""
        CREATE INDEX ix_blogpostmodel_variants_vuid
        ON blogpostmodel
        USING GIN ((variants -> 'vuid'));
    """)