# rxconfig.py (SOLO PARA DEPURACIÓN DE CORS - REVERTIR DESPUÉS)
import reflex as rx
from typing import List

class FullStackPythonConfig(rx.Config):
    app_name = "full_stack_python"
    api_url = "https://page-production-8756.up.railway.app" 

    cors_allowed_origins: List[str] = [
        "*" # <--- ¡CAMBIO TEMPORAL! Esto permite TODOS los orígenes.
            # DEBES REVERTIR ESTO UNA VEZ QUE FUNCIONE
    ]

    db_url = "sqlite:///reflex.db"

config = FullStackPythonConfig()