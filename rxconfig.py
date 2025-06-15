# rxconfig.py
import reflex as rx
from typing import List # AÑADE ESTA LÍNEA

class FullStackPythonConfig(rx.Config):
    app_name = "full_stack_python"
    api_url = "https://page-wpzf.onrender.com" # Tu URL de Render

    # CAMBIA ESTA LÍNEA para añadir la anotación de tipo
    cors_allowed_origins: List[str] = [ # <--- AQUI ESTÁ EL CAMBIO
        "http://localhost:3000",
        #"https://your-vercel-frontend-url.vercel.app", # ¡CAMBIA ESTO por la URL REAL de tu frontend en Vercel!
        "http://localhost:8000"
    ]

    db_url = "sqlite:///reflex.db"