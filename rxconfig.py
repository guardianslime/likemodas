import reflex as rx
import os
from dotenv import load_dotenv

load_dotenv()

# --- CORRECCIÓN AUTOMÁTICA DE BASE DE DATOS ---
# Si no encuentra la variable DATABASE_URL (ej. durante el build),
# asigna automáticamente una base de datos local para evitar errores.
database_url = os.getenv("DATABASE_URL")
if not database_url:
    database_url = "sqlite:///./reflex_build.db"

config = rx.Config(
    app_name="likemodas",
    show_built_with_reflex=False,
    db_url=database_url,  # Usamos la variable segura
    api_url=os.getenv("API_URL", "https://api.likemodas.com"),
    deploy_url=os.getenv("DEPLOY_URL", "https://www.likemodas.com"),
    
    # --- TUS CONFIGURACIONES DE CORS ---
    cors_allowed_origins=[
        "http://localhost:3000",
        "https://www.likemodas.com",
        "https://likemodas.com",
        "*", 
    ],
    
    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="medium",
        accent_color="violet",
        panel_background="translucent",
    ),
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
)