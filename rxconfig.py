import reflex as rx
import os
from typing import List, Optional, Dict, Any

# --- URLs de Producción ---
# URL del backend desplegado en Railway
BACKEND_PRODUCTION_URL = "https://web-production-15ad.up.railway.app"
# URL del frontend desplegado en Vercel
FRONTEND_PRODUCTION_URL = "https://full-stack-python-7h2v9smff-guardianslimes-projects.vercel.app"

class FullStackPythonConfig(rx.Config):
    app_name = "full_stack_python"
    telemetry_enabled = False
    frontend_port = 3000
    backend_port = 8000
    
    # --- Configuración de URLs ---
    api_url: str = os.getenv("API_URL", f"http://127.0.0.1:{backend_port}")
    deploy_url: str = os.getenv("FRONTEND_URL", f"http://localhost:{frontend_port}")

    # --- Configuración de CORS ---
    # Lista de orígenes permitidos para conectarse al backend
    cors_allowed_origins: List[str] = [
        f"http://localhost:{frontend_port}",
        BACKEND_PRODUCTION_URL,
        FRONTEND_PRODUCTION_URL,
    ]
    
    # --- Configuración de la Base de Datos ---
    db_url: str = os.getenv("DATABASE_URL", "sqlite:///reflex.db")
    tailwind: Optional[Dict[str, Any]] = None

config = FullStackPythonConfig()

