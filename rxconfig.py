# rxconfig.py (SOLUCIÓN DEFINITIVA)

import reflex as rx
import os

config = rx.Config(
    app_name="likemodas",
    
    # Lee la URL de la base de datos directamente desde la variable de entorno de Railway.
    # Si no existe, usa una local por defecto.
    db_url=os.getenv("DATABASE_URL", "postgresql://postgres:rszvQoEjlvQijlSTROgqCEDPiNdQqqmU@nozomi.proxy.rlwy.net:37918/railway"),

    # Define explícitamente los orígenes permitidos.
    # Esta es la forma más segura y compatible para evitar el error de despliegue.
    cors_allowed_origins=[
        "http://localhost:3000",
        # Asegúrate de que estas URLs coincidan con tu frontend y backend públicos
        "https://likemodas.com",
        "https://full-stack-python-production.up.railway.app",
    ],
    
    # El tema se mantiene igual.
    theme=rx.theme(
        appearance="dark",
        has_background=True,
        radius="medium",
        accent_color="violet",
    ),
)