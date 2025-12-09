from sqlmodel import create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# --- LÓGICA DE SEGURIDAD ---
# Si estamos en local (SQLite), usamos configuración simple.
if DATABASE_URL and "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
else:
    # Si estamos en producción (Postgres), usamos configuración robusta.
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"options": "-c timezone=utc"}, 
        pool_recycle=300
    )

def get_session():
    """Provee una sesión de base de datos segura."""
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()