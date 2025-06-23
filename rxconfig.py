import reflex as rx
import os
from typing import List, Optional, Dict, Any

# Define tus URLs de producción. Es una buena práctica tenerlas definidas.
# La URL donde vivirá tu backend (Railway)
BACKEND_PRODUCTION_URL = "https://web-production-15ad.up.railway.app"
# La URL donde vivirá tu frontend (Vercel)
# EN TU ARCHIVO ACTUALMENTE
# CÓDIGO CORREGIDO
FRONTEND_PRODUCTION_URL = "full-stack-python-git-main-guardianslimes-projects.vercel.app"  # ¡Asegúrate que esta sea tu URL de Vercel!

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
        BACKEND_PRODUCTION_URL,
        FRONTEND_PRODUCTION_URL,
    ]
    
    db_url: str = os.getenv("DATABASE_URL", "sqlite:///reflex.db")
    tailwind: Optional[Dict[str, Any]] = None

config = FullStackPythonConfig()
