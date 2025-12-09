import reflex as rx
import os
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURACIÓN DINÁMICA ---
# Si existe la variable de entorno, la usa. Si no, usa localhost.
# Esto permite que en Railway uses el dominio real y en tu PC uses localhost.
target_api_url = os.getenv("API_URL", "http://localhost:8000")
target_deploy_url = os.getenv("APP_BASE_URL", "http://localhost:3000")

config = rx.Config(
    app_name="likemodas",
    show_built_with_reflex=False,
    
    # Base de datos: Lee del entorno (SQLite en local, Postgres en Prod)
    db_url=os.getenv("DATABASE_URL", "sqlite:///reflex.db"),
    
    # URLs dinámicas
    api_url=target_api_url,
    deploy_url=target_deploy_url,
    
    cors_allowed_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "https://www.likemodas.com", # Permitir producción
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