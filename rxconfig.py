# rxconfig.py
import reflex as rx
from typing import List

class FullStackPythonConfig(rx.Config):
    app_name = "full_stack_python"
    api_url = "https://page-lb9g.onrender.com" # Tu URL del backend en Render (¡esta está bien!)

    cors_allowed_origins: List[str] = [
        "http://localhost:3000", # Para desarrollo local
        # ¡IMPORTANTE! Cambia esta línea para que sea la URL EXACTA de tu Vercel
        "https://pagefronted-zz96.vercel.app/", # <--- ¡ESTA ES LA URL CORREGIDA!
        "http://localhost:8000" # A veces necesario para el backend local
    ]

    db_url = "sqlite:///reflex.db"

config = FullStackPythonConfig()
