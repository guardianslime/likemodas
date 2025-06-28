import reflex as rx
import os
from typing import List, Optional, Dict, Any

# --- URLs de Producción ---
BACKEND_PRODUCTION_URL = "https://web-production-15ad.up.railway.app"

# Añadimos TODAS las posibles URLs de Vercel para máxima compatibilidad
FRONTEND_PRODUCTION_URL_LONG = "https://full-stack-python-7h2v9smff-guardianslimes-projects.vercel.app"
FRONTEND_PRODUCTION_URL_SHORT = "https://full-stack-python.vercel.app"

class FullStackPythonConfig(rx.Config):
    app_name = "full_stack_python"
    telemetry_enabled = False
    frontend_port = 3000
    backend_port = 8000

    api_url: str = os.getenv("API_URL", f"http://127.0.0.1:{backend_port}")
    deploy_url: str = os.getenv("FRONTEND_URL", f"http://localhost:{frontend_port}")

    # --- Configuración de CORS Definitiva ---
    cors_allowed_origins: List[str] = [
        f"http://localhost:{frontend_port}",
        BACKEND_PRODUCTION_URL,
        FRONTEND_PRODUCTION_URL_LONG,
        FRONTEND_PRODUCTION_URL_SHORT,
    ]

    db_url: str = os.getenv("DATABASE_URL", "sqlite:///reflex.db")
    tailwind: Optional[Dict[str, Any]] = None

config = FullStackPythonConfig()