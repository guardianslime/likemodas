from sqlmodel import create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()

# 1. Obtener la URL del entorno. Si falla, usar SQLite local por seguridad.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///reflex.db")

# 2. Configuración condicional del motor
if "sqlite" in DATABASE_URL:
    # Configuración simple para SQLite (Tu PC)
    # SQLite no soporta pool_recycle ni timezone args
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
else:
    # Configuración robusta para PostgreSQL (Hetzner/Railway)
    # PostgreSQL necesita estos argumentos para mantener la conexión viva
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"options": "-c timezone=utc"}, 
        pool_recycle=300
    )

def get_session():
    """
    Generador de sesión para inyección de dependencias.
    Maneja automáticamente el commit y el cierre.
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