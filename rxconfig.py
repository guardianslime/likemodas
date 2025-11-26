import reflex as rx
import os
from dotenv import load_dotenv

# Carga las variables de entorno locales
load_dotenv()

# 1. Base de datos (Lee la variable de Coolify o usa local)
database_url = os.getenv("DATABASE_URL", "sqlite:///reflex.db")

# 2. Configuración Dinámica de URLs
# API_URL: Es la dirección de tu servidor en Hetzner (Coolify).
# DEPLOY_URL: Es la dirección de tu web en Vercel.
target_api_url = os.getenv("API_URL", "http://localhost:8000")
target_deploy_url = os.getenv("DEPLOY_URL", "http://localhost:3000")

config = rx.Config(
    app_name="likemodas",
    show_built_with_reflex=False,
    
    db_url=database_url,
    
    # Aquí está la magia: Reflex usará lo que le digan las variables de entorno
    api_url=target_api_url,
    deploy_url=target_deploy_url,
    
    # Permisos de seguridad (CORS)
    cors_allowed_origins=[
        "http://localhost:3000",
        target_deploy_url,        # Permite a Vercel conectarse
        "https://likemodas.vercel.app", # (Opcional) Tu dominio futuro de Vercel
        "https://www.likemodas.com"     # (Opcional) Tu dominio real
    ],
    
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],

    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="medium",
        accent_color="violet",
        panel_background="translucent",
    ),
)