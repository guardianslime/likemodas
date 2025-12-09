# likemodas/db/session.py

from sqlmodel import create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Fallback por seguridad a SQLite si no encuentra nada
    DATABASE_URL = "sqlite:///reflex.db"

# [CORRECCIÓN] Configuración condicional del motor
# SQLite no soporta 'connect_args={"options": "-c timezone=utc"}' ni 'pool_recycle'
if "sqlite" in DATABASE_URL:
    # Configuración para SQLite (Local)
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
else:
    # Configuración para PostgreSQL (Producción/Railway)
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"options": "-c timezone=utc"}, 
        pool_recycle=300
    )

def get_session():
    """
    Provee una sesión de base de datos a través de la inyección de dependencias de FastAPI.
    Esto asegura un ciclo de vida de sesión limpio para cada petición.
    """
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()