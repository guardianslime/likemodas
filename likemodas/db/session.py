from sqlmodel import create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()

# Obtiene la URL. Si no hay, usa SQLite por defecto para evitar crashes locales.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///reflex.db")

# Configuración condicional del motor:
# - SQLite (Local): Sin argumentos complejos.
# - PostgreSQL (Railway): Con pool_recycle y timezone.
if "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"options": "-c timezone=utc"}, 
        pool_recycle=300
    )

def get_session():
    """
    Provee una sesión de base de datos a través de la inyección de dependencias.
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