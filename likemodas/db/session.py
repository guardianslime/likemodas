from sqlmodel import create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()

# Obtiene la URL del entorno
DATABASE_URL = os.getenv("DATABASE_URL")

# --- PROTECCIÓN PARA ENTORNO LOCAL ---
# Si tu PC lee "sqlite" del .env, usa configuración simple.
# Si el servidor lee "postgres", usa configuración robusta.
if DATABASE_URL and "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
else:
    # Configuración para Producción (Hetzner)
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