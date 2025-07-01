import reflex as rx
import os
from typing import List

# --- CORRECCIÓN CLAVE ---
# Lee las URLs desde las variables de entorno al inicio.
# Si la variable no existe (en desarrollo local), usa un valor por defecto.
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
DEPLOY_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


class FullStackPythonConfig(rx.Config):
    app_name = "full_stack_python"
    telemetry_enabled = False
    
    # Asigna las URLs leídas de las variables de entorno.
    api_url: str = API_URL
    deploy_url: str = DEPLOY_URL

    # Construye la lista de CORS dinámicamente a partir de las variables.
    # Esto permite que tu backend acepte peticiones de tu frontend.
    cors_allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        API_URL,
        DEPLOY_URL,
    ]
    
    db_url: str = os.getenv("DATABASE_URL", "sqlite:///reflex.db")

# Crea la instancia de la configuración.
config = FullStackPythonConfig()