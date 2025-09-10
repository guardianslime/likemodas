# rxconfig.py (VERSIÓN FINAL Y CORRECTA)

import reflex as rx
import os

# --- URLs de Despliegue ---
# Estas URLs se usan para configurar correctamente CORS y las redirecciones.

# La URL del backend en Railway. Reflex la necesita para que el frontend sepa a dónde conectarse.
RAILWAY_PUBLIC_URL = "https://full-stack-python-production.up.railway.app"

# El dominio final que verán tus usuarios.
PRODUCTION_DOMAIN = "https://www.likemodas.com"

# La URL de vista previa de Vercel para el frontend.
VERCEL_PREVIEW_URL = "https://full-stack-python.vercel.app"


# --- Configuración Principal de la Aplicación ---
config = rx.Config(
    app_name="likemodas",
    show_built_with_reflex=False,
    
    # Se usan las variables definidas arriba para las URLs de despliegue.
    api_url=RAILWAY_PUBLIC_URL,
    deploy_url=PRODUCTION_DOMAIN,
    
    # Orígenes permitidos para que el frontend pueda comunicarse con el backend.
    cors_allowed_origins=[
        "http://localhost:3000",
        PRODUCTION_DOMAIN,
        VERCEL_PREVIEW_URL,
    ],
    
    # --- CORRECCIÓN CLAVE ---
    # Se ha eliminado la línea `db_url`. 
    # Reflex leerá automáticamente la URL de la base de datos desde la variable 
    # de entorno `DATABASE_URL` proporcionada por Railway. Esto soluciona los
    # errores de conexión al unificar la configuración.
    
    # Se desactiva el plugin de sitemap que no es necesario para esta aplicación.
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],

    # Tema estético de la aplicación.
    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="medium",
        accent_color="violet",  # Color principal para elementos interactivos.
        panel_background="translucent",
    ),
)