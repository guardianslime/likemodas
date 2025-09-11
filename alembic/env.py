import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# --- INICIO DE CAMBIOS PARA REFLEX Y RAILWAY ---
# Añade la raíz del proyecto al path de Python para que pueda encontrar tus módulos.
sys.path.insert(0, os.getcwd())

# Importa la base de modelos de Reflex y tus modelos de aplicación.
# Esto es necesario para que target_metadata apunte a las tablas correctas.
import reflex as rx
from likemodas import models  # Asegúrate de que este import sea correcto para tu estructura.
# --- FIN DE CAMBIOS PARA REFLEX Y RAILWAY ---

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# --- INICIO DE LA MODIFICACIÓN CRÍTICA ---
# Obtiene la URL de la base de datos desde la variable de entorno de Railway.
# Esta es la única fuente de verdad para la conexión en producción.
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise ValueError("La variable de entorno DATABASE_URL no está configurada y es requerida para las migraciones.")

# Inyecta programáticamente la URL de la base de datos en la configuración de Alembic.
# Esto sobrescribe cualquier valor presente en alembic.ini.
config.set_main_option("sqlalchemy.url", database_url)
# --- FIN DE LA MODIFICACIÓN CRÍTICA ---

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = rx.Model.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

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

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()