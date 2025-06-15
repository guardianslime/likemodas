# rxconfig.py
import reflex as rx
from typing import List

class FullStackPythonConfig(rx.Config):
    app_name = "full_stack_python"
    api_url = "https://page-wpzf.onrender.com" 

    cors_allowed_origins: List[str] = [ 
        "http://localhost:3000",
        #"https://your-vercel-frontend-url.vercel.app", # ¡Recuerda cambiar esto!
        "http://localhost:8000"
    ]

    db_url = "sqlite:///reflex.db" 

# AÑADE ESTA LÍNEA AL FINAL DEL ARCHIVO:
config = FullStackPythonConfig() # <-- Instancia la clase de configuración que creaste