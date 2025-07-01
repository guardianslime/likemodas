import reflex as rx
import os

# --- URLs de Producción ---
# Estas son las URLs de tus servicios en la nube.
# Las leemos de las variables de entorno para que el código sea flexible.
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://full-stack-python-1dqv.vercel.app")
API_URL = os.getenv("API_URL", "https://web-production-50b7a.up.railway.app")

class FullStackPythonConfig(rx.Config):
    app_name = "full_stack_python"
    
    # Configura la URL de la API. En producción, usará la variable de Railway.
    # En tu PC, usará el valor por defecto si la variable no existe.
    api_url: str = API_URL
    
    # Configura la URL de despliegue del frontend.
    deploy_url: str = FRONTEND_URL
    
    # --- CORRECCIÓN CLAVE ---
    # La lista de orígenes permitidos para CORS.
    # Es crucial que la URL de Vercel esté aquí para que el backend acepte la conexión.
    cors_allowed_origins: list[str] = [
        "http://localhost:3000",  # Para desarrollo local
        FRONTEND_URL,             # ¡Para producción!
    ]
    
    # Configura la URL de la base de datos. En producción, usará la de Railway.
    db_url: str = os.getenv("DATABASE_URL", "sqlite:///reflex.db")

config = FullStackPythonConfig()
