# rxconfig.py (VERSIÓN FINAL Y CORRECTA)

import reflex as rx
import os

# La URL pública donde vivirá tu aplicación en Railway.
RAILWAY_PUBLIC_URL = "https://full-stack-python-production.up.railway.app"

# La URL final para tus usuarios.
PRODUCTION_DOMAIN = "https://www.likemodas.com"

# La URL de Vercel (opcional, pero bueno tenerla para CORS).
VERCEL_PREVIEW_URL = "https://full-stack-python.vercel.app"

# --- Configuración Principal Definitiva ---
config = rx.Config(
    app_name="likemodas",
    
    # 1. La URL REAL del backend para que el frontend se pueda conectar.
    #    Esto corrige el error "Cannot connect to server".
    api_url=RAILWAY_PUBLIC_URL,
    
    # 2. La URL PÚBLICA del frontend para generar los enlaces correctos.
    #    Esto corrige los enlaces para compartir.
    deploy_url=PRODUCTION_DOMAIN,
    
    # Lista blanca de dominios que tienen permiso para conectarse a tu backend.
    cors_allowed_origins=[
        "http://localhost:3000",
        PRODUCTION_DOMAIN,
        VERCEL_PREVIEW_URL,
    ],
    
    db_url="postgresql://postgres:rszvQoEjlvQijlSTROgqCEDPiNdQqqmU@nozomi.proxy.rlwy.net:37918/railway",
    
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],

    theme=rx.theme(
        appearance="dark",
        has_background=True,
        panel_background="solid",
        radius="medium",
        accent_color="sky"
    ),
)