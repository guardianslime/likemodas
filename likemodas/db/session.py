# likemodas/db/session.py (Versión Definitiva con Dependencia de FastAPI)

from sqlmodel import create_engine, Session
import os

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("La variable de entorno DATABASE_URL no está configurada.")

# Mantenemos el pool_recycle como una buena práctica de defensa
engine = create_engine(DATABASE_URL, connect_args={"options": "-c timezone=utc"}, pool_recycle=300)

# --- INICIO DE LA MODIFICACIÓN CRÍTICA ---
# Esta función ahora es un generador que FastAPI usará para inyectar la sesión.
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