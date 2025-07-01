import reflex as rx
import os
from typing import List

# --- URLs DE PRODUCCIÓN DEFINIDAS MANUALMENTE ---
# Esto elimina cualquier error de las variables de entorno.
FRONTEND_URL_PROD = "https://full-stack-python.vercel.app"
API_URL_PROD = "full-stack-python-production.up.railway.app"

class FullStackPythonConfig(rx.Config):
    app_name = "full_stack_python"
    telemetry_enabled = False
    frontend_port = 3000
    backend_port = 8000
    
    # Usa os.getenv para leer la URL de la API. En local usará el default.
    # En Vercel usará la variable de entorno que configuraremos.
    api_url: str = os.getenv("API_URL", f"http://127.0.0.1:{backend_port}")

    # La URL pública del frontend. En Vercel, esto vendrá de una variable de entorno.
    deploy_url: str = os.getenv("FRONTEND_URL", f"http://localhost:{frontend_port}")

    # El CORS debe permitir tu PC, y AMBAS URLs de producción.
    cors_allowed_origins: List[str] = [
        f"http://localhost:{frontend_port}",
        API_URL_PROD,
        FRONTEND_URL_PROD,
    ]
    
    db_url: str = os.getenv("DATABASE_URL", "sqlite:///reflex.db")

config = FullStackPythonConfig()
