# alembic/env.py (CÓDIGO CORRECTO Y DEFINITIVO)

from logging.config import fileConfig

# INICIO DE LA CORRECCIÓN CLAVE
import os
import sys
# Añade la ruta del directorio raíz del proyecto al sys.path
# Esto asegura que Alembic SIEMPRE pueda encontrar el módulo 'likemodas'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# FIN DE LA CORRECCIÓN

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import reflex as rx

# Ahora la importación funcionará 100% seguro
from likemodas import models

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = rx.Model.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()