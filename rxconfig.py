# rxconfig.py (SOLO PARA DEPURACIÓN DE CORS)
import reflex as rx
from typing import List

class FullStackPythonConfig(rx.Config):
    app_name = "full_stack_python"
    api_url = "https://page-lb9g.onrender.com"

    # TEMPORALMENTE para depurar CORS: permite *todos* los orígenes.
    # ¡NUNCA USAR ESTO EN PRODUCCIÓN REAL!
    cors_allowed_origins: List[str] = ["*"] 

    db_url = "sqlite:///reflex.db"

config = FullStackPythonConfig()
