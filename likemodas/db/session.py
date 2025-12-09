from sqlmodel import create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()

# Obtiene la URL. Si no hay, usa SQLite por defecto.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///reflex.db")

# Configuración del motor de base de datos
# Si es PostgreSQL (Producción), usamos los argumentos necesarios para estabilidad.
if "postgres" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"options": "-c timezone=utc"}, 
        pool_recycle=300
    )
# Si es SQLite (Local), usamos la configuración simple.
else:
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
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