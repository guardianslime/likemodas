# rxconfig.py
import reflex as rx
from typing import List

class FullStackPythonConfig(rx.Config):
    app_name = "full_stack_python"
    #api_url = "https://page-wpzf.onrender.com" # Tu URL del backend en Render

    cors_allowed_origins: List[str] = [
        "http://localhost:3000", # Para desarrollo local
        "https://pagefronted.vercel.app", # <--- ¡ESTA ES LA URL DE TU FRONTEND EN VERCEL!
        "http://localhost:8000" # A veces necesario para el backend local
    ]

    db_url = "sqlite:///reflex.db" 

config = FullStackPythonConfig()
