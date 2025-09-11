# likemodas/db/session.py

from contextlib import contextmanager
from sqlmodel import create_engine, Session
import os

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("La variable de entorno DATABASE_URL no está configurada.")
    
# Este motor es independiente del de Reflex
engine = create_engine(DATABASE_URL)

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