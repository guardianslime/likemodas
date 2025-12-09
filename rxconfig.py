import reflex as rx
import os
from dotenv import load_dotenv

load_dotenv()

# Obtenemos la URL de la base de datos
database_url = os.getenv("DATABASE_URL", "sqlite:///reflex.db")

# --- LÓGICA DE DETECCIÓN DE ENTORNO ---
# Si la base de datos es PostgreSQL (Producción), forzamos las URLs de producción.
# Esto arregla el error de WebSocket en Coolify.
if "postgres" in database_url:
    target_api_url = "https://www.likemodas.com"
    target_deploy_url = "https://www.likemodas.com"
else:
    # Si es SQLite (Local), usamos localhost
    target_api_url = "http://localhost:8000"
    target_deploy_url = "http://localhost:3000"

config = rx.Config(
    app_name="likemodas",
    show_built_with_reflex=False,
    
    # Base de datos
    db_url=database_url,
    
    # URLs definidas por la lógica de arriba
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