import reflex as rx
import os

# Lee las URLs de producción desde las variables de entorno.
# Si no existen, usa valores por defecto para el desarrollo local.
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

class FullStackPythonConfig(rx.Config):
    app_name = "simple_app" # Cambié esto para que coincida con tu código de ejemplo
    
    # Configura las URLs usando las variables leídas arriba.
    api_url: str = API_URL
    deploy_url: str = FRONTEND_URL
    
    # Lista de orígenes permitidos para CORS
    cors_allowed_origins: list[str] = [
        "http://localhost:3000",
        FRONTEND_URL,
    ]
    
    # Configuración de la base de datos
    db_url: str = os.getenv("DATABASE_URL", "sqlite:///reflex.db")

config = FullStackPythonConfig()
