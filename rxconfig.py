# rxconfig.py
import reflex as rx
from typing import List

class FullStackPythonConfig(rx.Config):
    app_name = "full_stack_python"
    # URL de tu backend en Render. Reflex usará HTTPS para API y WSS para WebSockets si esta es HTTPS.
    api_url = "https://page-lb9g.onrender.com" 

    cors_allowed_origins: List[str] = [
        "http://localhost:3000", # Para desarrollo local
        # ¡IMPORTANTE! Asegúrate de que esta URL de Vercel sea la EXACTA.
        # Le quitamos la barra final para consistencia.
        "https://pagefronted-zz96.vercel.app", # URL de tu frontend en Vercel
        "http://localhost:8000" # A veces necesario para el backend local
    ]

    db_url = "sqlite:///reflex.db" # Si estás usando SQLite

config = FullStackPythonConfig()

