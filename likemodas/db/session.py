from sqlmodel import create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()

# Obtiene la URL del entorno
DATABASE_URL = os.getenv("DATABASE_URL")

# --- LÓGICA DE SEGURIDAD PARA EXPORT LOCAL ---
# Si estamos en tu PC (SQLite), usamos configuración simple.
# Si estamos en Hetzner (Postgres), usamos configuración robusta.
if DATABASE_URL and "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
else:
    # Esto se ejecutará en Hetzner
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"options": "-c timezone=utc"}, 
        pool_recycle=300
    )

def get_session():
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()