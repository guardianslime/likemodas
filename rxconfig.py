import reflex as rx
import os
from dotenv import load_dotenv

# Carga las variables de entorno desde un archivo .env si existe (para desarrollo local)
load_dotenv()

# --- MODIFICACIÓN CRÍTICA ---
# Leemos explícitamente la variable de entorno DATABASE_URL.
# Si no la encuentra (como en tu entorno local), usará reflex.db por defecto.
# En Railway, SIEMPRE encontrará la variable y usará PostgreSQL.
database_url = os.getenv("DATABASE_URL", "sqlite:///reflex.db")
# --- FIN DE LA MODIFICACIÓN ---


# --- URLs de Despliegue ---
RAILWAY_PUBLIC_URL = "https://full-stack-python-production.up.railway.app"
PRODUCTION_DOMAIN = "https://www.likemodas.com"
VERCEL_PREVIEW_URL = "https://full-stack-python.vercel.app"


# --- Configuración Principal de la Aplicación ---
config = rx.Config(
    app_name="likemodas",
    show_built_with_reflex=False,
    
    # Asignamos explícitamente la URL de la base de datos que leímos arriba.
    db_url=database_url,
    
    api_url=RAILWAY_PUBLIC_URL,
    deploy_url=PRODUCTION_DOMAIN,
    
    cors_allowed_origins=[
        "http://localhost:3000",
        PRODUCTION_DOMAIN,
        VERCEL_PREVIEW_URL,
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