# likemodas/rxconfig.py (VERSIÓN FINAL Y CORRECTA)

import reflex as rx
import os
from dotenv import load_dotenv

# --- CORRECCIÓN CLAVE ---
# Carga las variables de entorno desde el archivo .env al inicio.
# Esto asegura que DATABASE_URL y otras claves estén disponibles
# para cualquier comando local de reflex (run, export, etc.).
load_dotenv()


# --- URLs de Despliegue ---
# Asegúrate de que estas URLs coincidan con tus servicios desplegados
RAILWAY_PUBLIC_URL = "https://tu-backend-en-railway.up.railway.app" # Reemplaza con tu URL de Railway
PRODUCTION_DOMAIN = "https://www.likemodas.com" # Tu dominio final
VERCEL_PREVIEW_URL = "https://tu-frontend-en-vercel.vercel.app" # Si usas Vercel para el frontend


# --- Configuración Principal de la Aplicación ---
config = rx.Config(
    app_name="likemodas",
    show_built_with_reflex=False,
    
    # URLs para la comunicación entre frontend y backend
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