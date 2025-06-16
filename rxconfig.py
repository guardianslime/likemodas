# rxconfig.py
import reflex as rx
from typing import List

class FullStackPythonConfig(rx.Config):
    app_name = "full_stack_python"
    api_url = "https://page-lb9g.onrender.com"

    cors_allowed_origins: List[str] = [
        "http://localhost:3000",
        "https://pagefronted-zz96.vercel.app", # <--- ¡VERIFICA ESTA LÍNEA EN GITHUB!
        "http://localhost:8000"
    ]

    db_url = "sqlite:///reflex.db"

config = FullStackPythonConfig()
