import reflex as rx
import os
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv("DATABASE_URL", "sqlite:///reflex.db")
target_api_url = os.getenv("API_URL", "http://localhost:8000")

config = rx.Config(
    app_name="likemodas",
    show_built_with_reflex=False,
    db_url=database_url,
    api_url=target_api_url,
    
    # --- CORRECCIÓN DE CORS ---
    cors_allowed_origins=[
        "http://localhost:3000",
        "https://www.likemodas.com",
        "https://likemodas.com",
        "https://full-stack-python.vercel.app",
        # Añadimos comodín para subdominios de vercel por si acaso
        "https://*.vercel.app" 
    ],
    # ---------------------------
    
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="medium",
        accent_color="violet",
        panel_background="translucent",
    ),
)