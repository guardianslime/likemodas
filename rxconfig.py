import reflex as rx
import os

# --- LECTURA DE VARIABLES DE ENTORNO ---
# Lee la URL del frontend (para CORS en el backend). Usa un valor por defecto para desarrollo local.
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Lee la URL del backend (para que el frontend sepa a dónde conectar).
# Lee "API_URL", que es el nombre de la variable que configuraste en Vercel.
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


class FullStackPythonConfig(rx.Config):
    # --- CORRECCIÓN CLAVE 1 ---
    # El nombre de la app DEBE coincidir con el nombre de tu carpeta principal de código.
    app_name = "full_stack_python" 
    
    # Configura las URLs usando las variables leídas arriba.
    api_url: str = API_URL
    deploy_url: str = FRONTEND_URL
    
    # Lista de orígenes permitidos para CORS.
    # Esto permite que tu frontend en Vercel se conecte al backend.
    cors_allowed_origins: list[str] = [
        FRONTEND_URL,
        "http://localhost:3000",
    ]
    
    # Configuración de la base de datos.
    db_url: str = os.getenv("DATABASE_URL", "sqlite:///reflex.db")

    # --- CORRECCIÓN CLAVE 2 ---
    # Hemos eliminado la línea "socket: str = ..." que causaba el conflicto.
    # Ahora Reflex usará su configuración por defecto, que es la correcta.

config = FullStackPythonConfig()
