import reflex as rx
import os

# --- URLs DE PRODUCCIÓN DEFINIDAS MANUALMENTE ---
# Esto elimina cualquier error de las variables de entorno.
FRONTEND_URL_PROD = "https://frontedpage-t5mu.vercel.app"
API_URL_PROD = "https://web-production-50b7a.up.railway.app"

class FullStackPythonConfig(rx.Config):
    # --- CORRECCIÓN CLAVE ---
    # El nombre de la app DEBE coincidir con el nombre de tu carpeta de código.
    app_name = "full_stack_python"
    
    api_url: str = API_URL_PROD
    deploy_url: str = FRONTEND_URL_PROD
    
    cors_allowed_origins: list[str] = [
        FRONTEND_URL_PROD,
        "http://localhost:3000",
    ]
    
    db_url: str = os.getenv("DATABASE_URL", "sqlite:///reflex.db")

config = FullStackPythonConfig()
