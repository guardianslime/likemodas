"""add_variant_uuid_to_products

Revision ID: 78607dfddef5
Revises: 172f3dff76ac
Create Date: 2025-09-21 17:04:24.587021

"""
from typing import Sequence, Union
import uuid
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
    """Adds variant_uuid to existing product variants."""
    conn = op.get_bind()
    meta = sa.MetaData()
    meta.reflect(bind=conn)
    blogpostmodel_table = sa.Table('blogpostmodel', meta)

    results = conn.execute(sa.select(blogpostmodel_table)).fetchall()

    for post in results:
        if not post.variants or not isinstance(post.variants, list):
            continue

        updated_variants = []
        needs_update = False
        for variant in post.variants:
            if isinstance(variant, dict) and 'variant_uuid' not in variant:
                variant['variant_uuid'] = str(uuid.uuid4())
                needs_update = True
            updated_variants.append(variant)

        if needs_update:
            conn.execute(
                blogpostmodel_table.update()
                .where(blogpostmodel_table.c.id == post.id)
                .values(variants=updated_variants)
            )

def downgrade() -> None:
    """Removes variant_uuid from product variants (optional)."""
    # El downgrade es opcional, lo dejamos así por seguridad.
    pass