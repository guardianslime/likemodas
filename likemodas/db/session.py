# likemodas/db/session.py

from sqlmodel import create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# --- CORRECCIÓN CRÍTICA ---
# Si no hay variable de entorno (ej. durante el 'reflex export'),
# asignamos una base de datos SQLite temporal para evitar el error "got None".
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./build_dummy.db"

# --- LÓGICA DE CONEXIÓN ---
# Si es SQLite (local o build), usamos configuración simple.
if "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
else:
    # Si es Postgres (Producción/Hetzner), usamos la configuración robusta.
    engine = create_engine(
        DATABASE_URL, 
        # connect_args={"options": "-c timezone=utc"}, # Descomenta si usas Postgres y necesitas UTC forzado
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