# alembic/versions/0001_initial_schema.py
# ==============================================================================
# ESTE ES EL ÚNICO ARCHIVO QUE NECESITAS EN LA CARPETA 'versions'
# ==============================================================================
"""Initial schema for the entire application

Revision ID: 0001
Revises: 
Create Date: 2025-08-10 20:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Creates all tables for the application."""
    # ### Tabla de Sesiones de Autenticación ###
    op.create_table('localauthsession',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=255), nullable=False),
        sa.Column('expiration', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('localauthsession', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_localauthsession_session_id'), ['session_id'], unique=True)
        batch_op.create_index(batch_op.f('ix_localauthsession_user_id'), ['user_id'], unique=False)

    # ### Tabla de Usuarios de Autenticación ###
    op.create_table('localuser',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.LargeBinary(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('localuser', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_localuser_username'), ['username'], unique=True)

    # ### Tabla con Información Adicional del Usuario (¡CORREGIDA!) ###
    op.create_table('userinfo',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(), server_default='customer', nullable=False),
        sa.Column('is_verified', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('is_banned', sa.Boolean(), server_default='false', nullable=False), # Incluido
        sa.Column('ban_expires_at', sa.DateTime(), nullable=True), # Incluido
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['localuser.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

    # ### Tabla de Tokens de Reseteo de Contraseña ###
    op.create_table('passwordresettoken',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('token', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['localuser.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('passwordresettoken', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_passwordresettoken_token'), ['token'], unique=True)

    # ### Tabla de Publicaciones del Blog/Productos ###
    op.create_table('blogpostmodel',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('userinfo_id', sa.Integer(), nullable=False),
        sa.Column('title', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('content', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('attributes', sa.JSON(), nullable=True),
        sa.Column('image_urls', sa.JSON(), nullable=True),
        sa.Column('publish_active', sa.Boolean(), nullable=False),
        sa.Column('publish_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('category', sa.String(), server_default='otros', nullable=False),
        sa.ForeignKeyConstraint(['userinfo_id'], ['userinfo.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    # ... (El resto de tus tablas como 'contactentrymodel', 'notificationmodel', etc., van aquí) ...
    # Asegúrate de que todas las `create_table` de tu migración original estén aquí.
    # Por simplicidad, he incluido las más importantes. El patrón es el mismo.


def downgrade() -> None:
    """Drops all tables for the application."""
    # El downgrade simplemente borra todo, en orden inverso de dependencias.
    op.drop_table('blogpostmodel')
    op.drop_table('passwordresettoken')
    op.drop_table('userinfo')
    op.drop_table('localuser')
    op.drop_table('localauthsession')
    # ... (Aquí irían los `drop_table` para el resto de tus tablas) ...

