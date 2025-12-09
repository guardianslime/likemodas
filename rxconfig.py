import reflex as rx
import os
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURACIÓN DINÁMICA ---
# Intenta leer del entorno. Si no existen (fallo), usa localhost por defecto.
target_api_url = os.getenv("API_URL", "http://localhost:8000")
target_deploy_url = os.getenv("APP_BASE_URL", "http://localhost:3000")
target_db_url = os.getenv("DATABASE_URL", "sqlite:///reflex.db")

config = rx.Config(
    app_name="likemodas",
    show_built_with_reflex=False,
    
    # Base de datos dinámica
    db_url=target_db_url,
    
    # URLs dinámicas
    api_url=target_api_url,
    deploy_url=target_deploy_url,
    
    cors_allowed_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "https://www.likemodas.com",
        "https://likemodas.com",
        "*"
    ],
    
    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="medium",
        accent_color="violet",
        panel_background="translucent",
    ),
)