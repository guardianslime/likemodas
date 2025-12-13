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
    # --- CAMBIO DE SEGURIDAD: CORS RESTRICTIVO (CORREGIDO) ---
    cors_allowed_origins=[
        "http://localhost:3000",
        "https://www.likemodas.com",
        "https://likemodas.com",
        # NECESARIO: Permitir todo (*) temporalmente para que la App y WebViews conecten
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