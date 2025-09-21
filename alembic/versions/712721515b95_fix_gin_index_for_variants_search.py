"""fix_gin_index_for_variants_search_and_change_type_to_jsonb

Revision ID: 712721515b95
Revises: 057ac65d952b
Create Date: 2025-09-21 14:49:46.779120

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '712721515b95'
down_revision: Union[str, Sequence[str], None] = '057ac65d952b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Paso 1: Cambiar el tipo de la columna de JSON a JSONB.
    # El 'USING variants::text::jsonb' es crucial para que PostgreSQL convierta los datos existentes.
    op.alter_column('blogpostmodel', 'variants',
               existing_type=postgresql.JSON(),
               type_=postgresql.JSONB(),
               postgresql_using='variants::text::jsonb')

    # Paso 2: Intentar eliminar el índice antiguo e incorrecto, si es que existe.
    op.execute("DROP INDEX IF EXISTS ix_blogpostmodel_variants_vuid")

    # Paso 3: Crear el nuevo y correcto índice GIN sobre la columna ya convertida a JSONB.
    op.create_index(
        'ix_blogpostmodel_variants',
        'blogpostmodel',
        ['variants'],
        unique=False,
        postgresql_using='gin'
    )


def downgrade() -> None:
    # Para revertir, hacemos los pasos en orden inverso.
    # Paso 1: Eliminar el nuevo índice GIN.
    op.execute("DROP INDEX IF EXISTS ix_blogpostmodel_variants")
    
    # Paso 2: Recrear el índice antiguo (aunque sea incorrecto, es para reversibilidad).
    op.execute("""
        CREATE INDEX ix_blogpostmodel_variants_vuid
        ON blogpostmodel
        USING GIN ((variants -> 'vuid'));
    """)

    # Paso 3: Cambiar el tipo de la columna de vuelta a JSON.
    op.alter_column('blogpostmodel', 'variants',
               existing_type=postgresql.JSONB(),
               type_=postgresql.JSON(),
               postgresql_using='variants::text::json')