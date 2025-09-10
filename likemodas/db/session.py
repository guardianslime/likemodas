# likemodas/db/session.py
from contextlib import contextmanager
from sqlmodel import create_engine, Session
import os

# ANTES: DATABASE_URL = os.getenv("DB_URL")
# AHORA: Lee la misma variable que usa Reflex
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Esto te avisará si la variable no está configurada por alguna razón
    raise ValueError("La variable de entorno DATABASE_URL no está configurada.")
    
engine = create_engine(DATABASE_URL)

@contextmanager
def get_db_session():
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()