# rxconfig.py (SOLUCIÓN FINAL)

import reflex as rx
import os

# --- Configuración Principal ---
config = rx.Config(
    app_name="likemodas",

    # Lee la URL de la base de datos directamente desde la variable de entorno de Railway.
    # Si no existe, usa una local por defecto.
    db_url=os.getenv("DATABASE_URL", "sqlite:///reflex.db"),

    # Define explícitamente los orígenes permitidos.
    # Esta es la forma más segura y compatible para evitar el error.
    cors_allowed_origins=[
        "http://localhost:3000",
        # Añade aquí la URL PÚBLICA de tu frontend en Vercel/Railway
        # Ejemplo: "https://mi-tienda.vercel.app"
        "https://likemodas.com", 
        # Añade aquí la URL PÚBLICA de tu backend en Railway
        # Ejemplo: "https://likemodas-backend.up.railway.app"
        "https://full-stack-python-production.up.railway.app"
    ],

    # El tema se mantiene igual.
    theme=rx.theme(
        appearance="dark",
        has_background=True,
        radius="medium",
        accent_color="violet",
    ),
)