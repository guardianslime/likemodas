"""add_variant_uuid_to_products

Revision ID: 78607dfddef5
Revises: 172f3dff76ac
Create Date: 2025-09-21 17:04:24.587021

"""
from typing import Sequence, Union
import uuid
import time
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '78607dfddef5'
down_revision: Union[str, Sequence[str], None] = '172f3dff76ac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    [VERSIÓN CORREGIDA]
    Adds variant_uuid to existing product variants by processing them in batches
    to prevent database connection timeouts on long-running operations.
    """
    conn = op.get_bind()
    meta = sa.MetaData()
    meta.reflect(bind=conn)
    blogpostmodel_table = sa.Table('blogpostmodel', meta)

    # Obtenemos solo los IDs de los posts para iterar sobre ellos.
    # Esto es mucho más eficiente en memoria que cargar todos los posts completos.
    post_ids = [row[0] for row in conn.execute(sa.select(blogpostmodel_table.c.id)).fetchall()]
    
    total_posts = len(post_ids)
    print(f"Se encontraron {total_posts} productos para revisar.")

    for i, post_id in enumerate(post_ids):
        # Por cada ID, obtenemos solo las variantes de ese producto específico.
        post_variants = conn.execute(
            sa.select(blogpostmodel_table.c.variants).where(blogpostmodel_table.c.id == post_id)
        ).scalar_one_or_none()

        if not post_variants or not isinstance(post_variants, list):
            continue

        updated_variants = []
        needs_update = False
        for variant in post_variants:
            if isinstance(variant, dict) and 'variant_uuid' not in variant:
                variant['variant_uuid'] = str(uuid.uuid4())
                needs_update = True
            updated_variants.append(variant)

        if needs_update:
            # Si se hicieron cambios, actualizamos solo esta fila.
            conn.execute(
                blogpostmodel_table.update()
                .where(blogpostmodel_table.c.id == post_id)
                .values(variants=updated_variants)
            )
            print(f"({i+1}/{total_posts}) - Producto ID #{post_id} actualizado.")
            # Pequeña pausa para no saturar la conexión
            time.sleep(0.05)

    print("Migración de datos de variantes completada.")


def downgrade() -> None:
    """Downgrade is optional and can be left empty for data migrations."""
    pass