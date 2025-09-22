"""populate_variant_uuid_for_existing_products

Revision ID: 9449226f6f89
Revises: 76966806eea6
Create Date: 2025-09-21 21:35:00.000000

"""
from typing import Sequence, Union
import uuid
import time
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '<EL_SEGUNDO_NUEVO_ID>' # Reemplaza esto
down_revision: Union[str, Sequence[str], None] = '<EL_ID_DE_LA_MIGRACION_ANTERIOR_(GIN_INDEX)>' # Reemplaza esto
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    conn = op.get_bind()
    meta = sa.MetaData()
    meta.reflect(bind=conn)
    blogpostmodel_table = sa.Table('blogpostmodel', meta)
    post_ids = [row[0] for row in conn.execute(sa.select(blogpostmodel_table.c.id)).fetchall()]

    if not post_ids:
        print("No products found to migrate.")
        return

    for post_id in post_ids:
        post_variants = conn.execute(sa.select(blogpostmodel_table.c.variants).where(blogpostmodel_table.c.id == post_id)).scalar_one_or_none()
        if not post_variants or not isinstance(post_variants, list): continue

        updated_variants, needs_update = [], False
        for variant in post_variants:
            if isinstance(variant, dict) and 'variant_uuid' not in variant:
                variant['variant_uuid'] = str(uuid.uuid4())
                needs_update = True
            updated_variants.append(variant)

        if needs_update:
            conn.execute(
                blogpostmodel_table.update().where(blogpostmodel_table.c.id == post_id).values(variants=updated_variants)
            )

def downgrade() -> None:
    pass