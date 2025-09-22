"""add_qr_system_support_gin_index_and_uuid

Revision ID: 48bbdd8a086f
Revises: 7691cf96710b
Create Date: 2025-09-21 21:51:37.066661

"""
from typing import Sequence, Union
import uuid
import time
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '48bbdd8a086f'
down_revision: Union[str, Sequence[str], None] = '7691cf96710b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Realiza dos tareas críticas para el nuevo sistema de QR:
    1. Crea un índice GIN en la columna 'variants' para búsquedas de alto rendimiento.
    2. Itera sobre todos los productos existentes para añadir un 'variant_uuid' único
       a cada variante, asegurando la compatibilidad con el sistema de URLs.
    """
    # ### PASO 1: Crear el índice GIN para búsquedas eficientes ###
    print("Creando el índice GIN en la columna blogpostmodel.variants...")
    op.create_index(
        'ix_blogpostmodel_variants_gin',
        'blogpostmodel',
        ['variants'],
        unique=False,
        postgresql_using='gin'
    )
    print("Índice GIN creado exitosamente.")

    # ### PASO 2: Migrar datos para añadir variant_uuid ###
    print("Iniciando migración de datos para añadir variant_uuid a las variantes de productos...")
    conn = op.get_bind()
    meta = sa.MetaData()
    meta.reflect(bind=conn)
    blogpostmodel_table = sa.Table('blogpostmodel', meta)

    post_ids = [row[0] for row in conn.execute(sa.select(blogpostmodel_table.c.id)).fetchall()]
    
    total_posts = len(post_ids)
    if not total_posts:
        print("No se encontraron productos para migrar. Paso de migración de datos omitido.")
        return

    print(f"Se encontraron {total_posts} productos para revisar.")
    updated_count = 0

    for i, post_id in enumerate(post_ids):
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
            conn.execute(
                blogpostmodel_table.update().where(blogpostmodel_table.c.id == post_id).values(variants=updated_variants)
            )
            updated_count += 1
            print(f"  ({i + 1}/{total_posts}) - Producto ID #{post_id} actualizado.")
            time.sleep(0.05)
            
    print(f"Migración de datos completa. Se actualizaron {updated_count} productos.")


def downgrade() -> None:
    """Revierte los cambios de la función upgrade."""
    # ### Revertir PASO 1: Eliminar el índice GIN ###
    print("Eliminando el índice GIN ix_blogpostmodel_variants_gin...")
    op.drop_index('ix_blogpostmodel_variants_gin', table_name='blogpostmodel')
    print("Índice GIN eliminado.")
    
    # El downgrade para la migración de datos se omite por seguridad.
    pass