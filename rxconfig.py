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
    api_url: str = "/backend"

    cors_allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    # ¡CAMBIO IMPORTANTE!
    # Lee la URL de la base de datos desde las variables de entorno de Railway.
    # Si no la encuentra, usa SQLite para desarrollo local.
    db_url: str = os.getenv("DATABASE_URL", "sqlite:///reflex.db")

config = FullStackPythonConfig()