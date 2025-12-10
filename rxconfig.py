import reflex as rx
import os
from dotenv import load_dotenv

load_dotenv()

config = rx.Config(
    app_name="likemodas",
    show_built_with_reflex=False,
    db_url=os.getenv("DATABASE_URL"),
    api_url=os.getenv("API_URL", "https://api.likemodas.com"),
    deploy_url=os.getenv("DEPLOY_URL", "https://www.likemodas.com"),
    
    # --- CAMBIO DE SEGURIDAD: CORS RESTRICTIVO ---
    cors_allowed_origins=[
        "http://localhost:3000",        # Desarrollo local
        "https://www.likemodas.com",    # Producción
        "https://likemodas.com",        # Producción sin www
        # La App móvil no usa CORS, así que no necesita estar aquí.
    ],
    
    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="medium",
        accent_color="violet",
        panel_background="translucent",
    ),
)