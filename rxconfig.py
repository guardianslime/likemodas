# rxconfig.py
import reflex as rx
import os
from typing import List

class FullStackPythonConfig(rx.Config):
    """Clase de configuración para tu aplicación Reflex."""

    app_name = "full_stack_python"
    telemetry_enabled = False
    frontend_port = 3000
    backend_port = 8000

    # ¡SOLUCIÓN! Añadimos la URL de despliegue.
    # Esto es necesario para la generación del sitemap y otros metadatos.
    # Puedes poner un placeholder si aún no tienes la URL final de Railway.
    deploy_url: str = "https://example.com"

    api_url: str = "/backend"

    cors_allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    db_url: str = os.getenv("DATABASE_URL", "sqlite:///reflex.db")

config = FullStackPythonConfig()