import reflex as rx
import os
from typing import List, Optional, Dict, Any

# Define tu URL de producción aquí una sola vez.
# Esto hace que sea más fácil de cambiar en el futuro.
PRODUCTION_URL = "https://web-production-15ad.up.railway.app"

class FullStackPythonConfig(rx.Config):
    app_name = "full_stack_python"
    telemetry_enabled = False
    frontend_port = 3000
    backend_port = 8000
    
    # Usa la variable de entorno para la URL de la API.
    # Si no existe (en tu PC), usa la URL local por defecto.
    api_url: str = os.getenv("API_URL", f"http://127.0.0.1:{backend_port}")

    # Usa la variable de entorno para la URL de despliegue.
    # Si no existe, usa la URL del frontend local por defecto.
    deploy_url: str = os.getenv("FRONTEND_URL", f"http://localhost:{frontend_port}")

    # ¡MUY IMPORTANTE! El CORS debe permitir tanto tu PC como Railway.
    cors_allowed_origins: List[str] = [
        f"http://localhost:{frontend_port}",  # Para desarrollo local
        PRODUCTION_URL,                      # Para tu sitio en producción
    ]
    
    db_url: str = os.getenv("DATABASE_URL", "sqlite:///reflex.db")

    tailwind: Optional[Dict[str, Any]] = None

config = FullStackPythonConfig()