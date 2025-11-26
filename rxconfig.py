import reflex as rx
import os
from dotenv import load_dotenv

load_dotenv()

# URLs
database_url = os.getenv("DATABASE_URL", "sqlite:///reflex.db")
target_api_url = os.getenv("API_URL", "https://api.likemodas.com") # Forzamos la URL correcta aquí por si acaso

config = rx.Config(
    app_name="likemodas",
    show_built_with_reflex=False,
    
    db_url=database_url,
    api_url=target_api_url,
    
    # --- LA SOLUCIÓN: PERMISOS TOTALES ---
    # Esto permite que Vercel (y cualquier subdominio) se conecte sin bloqueo.
    cors_allowed_origins=[
        "*"
    ],
    # -------------------------------------
    
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],

    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="medium",
        accent_color="violet",
        panel_background="translucent",
    ),
)