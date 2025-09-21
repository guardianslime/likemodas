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
    # Usamos "DROP INDEX IF EXISTS". Este comando nunca fallará,
    # por lo que la transacción no se abortará.
    op.execute("DROP INDEX IF EXISTS ix_blogpostmodel_variants_vuid")

    # Ahora que la transacción está segura, creamos el nuevo índice.
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
    # También usamos "IF EXISTS" aquí por seguridad.
    op.execute("DROP INDEX IF EXISTS ix_blogpostmodel_variants")

    # Recrea el índice antiguo que existía antes
    op.execute("""
        CREATE INDEX ix_blogpostmodel_variants_vuid
        ON blogpostmodel
        USING GIN ((variants -> 'vuid'));
    """)