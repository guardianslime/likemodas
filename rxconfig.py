# rxconfig.py
import reflex as rx
import os
from typing import List

class FullStackPythonConfig(rx.Config):
    app_name = "full_stack_python"
    telemetry_enabled = False
    frontend_port = 3000
    backend_port = 8000
    deploy_url: str = "https://web-production-15ad.up.railway.app" # Esto ya no es tan crítico aquí
    api_url: str = "" # La API se sirve desde la raíz ahora

    # ¡CAMBIO IMPORTANTE! Preparamos la lista para aceptar la URL de Vercel.
    cors_allowed_origins: List[str] = [
        "http://localhost:3000", # Para tu desarrollo local del frontend
        "https://mi-frontend.vercel.app", # Placeholder para tu futura URL de Vercel
    ]
    
    db_url: str = os.getenv("DATABASE_URL", "sqlite:///reflex.db")

config = FullStackPythonConfig()
