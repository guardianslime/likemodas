from sqlmodel import create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()

# Obtiene la URL. Si falla, usa una por defecto para que no crashee la compilación local
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///reflex.db")

# Esta pequeña validación es necesaria porque SQLite NO soporta los argumentos de Postgres.
# Esto no afecta al hosting (porque allá usará Postgres), pero salva tu entorno local.
if "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
else:
    # Configuración optimizada para Producción (Hetzner/Coolify)
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"options": "-c timezone=utc"}, 
        pool_recycle=300
    )

def get_session():
    """
    Provee una sesión de base de datos segura.
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