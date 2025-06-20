# rxconfig.py
import reflex as rx
from typing import List

class FullStackPythonConfig(rx.Config):
    app_name = "full_stack_python"
    # ¡ESTA DEBE SER LA URL DE RAILWAY, SIN BARRA FINAL!
    api_url = "https://page-production-8756.up.railway.app" 

    cors_allowed_origins: List[str] = [
        "http://localhost:3000",
        # ¡ESTA ES LA URL DE TU FRONTEND DE VERCEL, SIN BARRA FINAL!
        "https://frontend-snowy-six-69.vercel.app",
        "http://localhost:8000"
    ]

    db_url = "sqlite:///reflex.db"
config = FullStackPythonConfig()