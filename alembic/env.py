# alembic/env.py
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Importamos reflex, que contiene la clase base rx.Model.
import reflex as rx 

# Lee la URL de la base de datos desde la variable de entorno
DATABASE_URL = os.getenv("DATABASE_URL")


# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Usamos rx.Model.metadata, que es el lugar correcto donde
# Alembic puede encontrar todas las definiciones de tus tablas.
target_metadata = rx.Model.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    """
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
    """Run migrations in 'online' mode.
    """
    configuration = context.config
    if DATABASE_URL:
        configuration.set_main_option("sqlalchemy.url", DATABASE_URL)
        
    # --- INICIO DE LA CORRECCIÓN ---
    # Esta es la sección que tenía el error de tipeo.
    # Ahora usamos "configuration.main_section" para obtener la
    # sección de configuración correcta.
    connectable = engine_from_config(
        configuration.get_section(configuration.main_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    # --- FIN DE LA CORRECCIÓN ---

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