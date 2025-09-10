# rxconfig.py (VERSIÓN FINAL Y CORRECTA)

import reflex as rx
import os
from dotenv import load_dotenv

# --- CORRECCIÓN CLAVE ---
# Carga las variables de entorno desde el archivo .env al inicio.
# Esto asegura que DATABASE_URL y otras claves estén disponibles
# para cualquier comando local de reflex (run, export, etc.).
load_dotenv()


# --- URLs de Despliegue ---
RAILWAY_PUBLIC_URL = "https://full-stack-python-production.up.railway.app"
PRODUCTION_DOMAIN = "https://www.likemodas.com"
VERCEL_PREVIEW_URL = "https://full-stack-python.vercel.app"


# --- Configuración Principal de la Aplicación ---
config = rx.Config(
    app_name="likemodas",
    show_built_with_reflex=False,
    
    api_url=RAILWAY_PUBLIC_URL,
    deploy_url=PRODUCTION_DOMAIN,
    
    cors_allowed_origins=[
        "http://localhost:3000",
        PRODUCTION_DOMAIN,
        VERCEL_PREVIEW_URL,
    ],
    
    # Ya no definimos db_url aquí. Reflex usará la variable de entorno DATABASE_URL
    # que acabamos de cargar con load_dotenv().
    
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],

    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="medium",
        accent_color="violet",
        panel_background="translucent",
    ),
)