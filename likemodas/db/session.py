# likemodas/db/session.py (Versión Mejorada)

from contextlib import contextmanager
from sqlmodel import create_engine, Session
import os

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("La variable de entorno DATABASE_URL no está configurada.")

# Se añade pool_recycle para mejorar la resiliencia en entornos de producción.
# Este valor debe ser menor que el timeout de inactividad de tu proveedor de BD.
engine = create_engine(DATABASE_URL, connect_args={"options": "-c timezone=utc"}, pool_recycle=3600)

@contextmanager
def get_db_session():
    """Provee una sesión de base de datos cruda y se asegura de que se cierre."""
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()