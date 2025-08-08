import reflex as rx
import os

# --- URLs de la aplicación ---
API_URL = os.getenv("API_URL", "http://localhost:8000")
DEPLOY_URL = os.getenv("DEPLOY_URL", "http://localhost:3000")

# URLs de despliegue adicionales
VERCEL_LEGACY_URL = "https://full-stack-python.vercel.app"
LIKEMODAS_URL = "https://www.likemodas.com"

# --- Orígenes CORS permitidos ---
default_origins = [
    "http://localhost:3000",
    API_URL,
    DEPLOY_URL,
    VERCEL_LEGACY_URL, # URL añadida para Vercel
    LIKEMODAS_URL,     # URL del dominio principal
]
additional_origins = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
cors_allowed_origins = list(
    {
        origen.strip()
        for origen in default_origins + additional_origins
        if origen.strip()
    }
)

# --- Configuración Principal Unificada ---
config = rx.Config(
    app_name="likemodas",
    db_url="postgresql://postgres:rszvQoEjlvQijlSTROgqCEDPiNdQqqmU@nozomi.proxy.rlwy.net:37918/railway",
    api_url=API_URL,
    cors_allowed_origins=cors_allowed_origins,
    
    # Desactiva el plugin de sitemap para eliminar la advertencia
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
    
    # Tema unificado para toda la aplicación
    theme=rx.theme(
        appearance="dark",
        has_background=True,
        panel_background="solid",
        radius="medium",
        accent_color="sky"
    ),
)