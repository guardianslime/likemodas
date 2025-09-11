import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# --- INICIO DE CAMBIOS PARA REFLEX ---
# Añade la raíz del proyecto al path de Python para que pueda encontrar tus módulos.
# Esto asume que tu alembic.ini está en la carpeta raíz del proyecto.
sys.path.insert(0, os.getcwd())

# Importa la base de modelos de Reflex y tu archivo de modelos
import reflex as rx
from likemodas import models
# --- FIN DE CAMBIOS PARA REFLEX ---


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# --- INICIO DE LA MODIFICACIÓN CLAVE ---
# Lee la URL de la base de datos desde la variable de entorno,
# asegurando que las migraciones y la app principal usen la misma conexión.
# Esta es la única fuente de verdad.
db_url = os.getenv("DATABASE_URL")

# Si por alguna razón la variable de entorno no está disponible,
# intenta usar la del archivo .ini como respaldo.
if not db_url:
    db_url = config.get_main_option("sqlalchemy.url")

# Si después de todo no hay URL, lanza un error claro.
if not db_url:
    raise ValueError(
        "La URL de la base de datos no está configurada. "
        "Defínela en la variable de entorno DATABASE_URL o en alembic.ini."
    )

# Establece la URL correcta para que el resto del script la utilice.
config.set_main_option("sqlalchemy.url", db_url)
# --- FIN DE LA MODIFICACIÓN CLAVE ---


# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- CAMBIO CLAVE ---
# Reemplaza 'target_metadata = None' con esto para apuntar a los modelos de Reflex.
target_metadata = rx.Model.metadata
# --- FIN DEL CAMBIO CLAVE ---


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
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
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()