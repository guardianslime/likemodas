# rxconfig.py (Versión Final y Corregida)

import reflex as rx
import os

# La URL pública donde vivirá tu aplicación en Railway.
RAILWAY_PUBLIC_URL = "https://full-stack-python-production.up.railway.app"

# La URL final para tus usuarios.
PRODUCTION_DOMAIN = "https://www.likemodas.com"

# La URL de Vercel.
VERCEL_PREVIEW_URL = "https://full-stack-python.vercel.app"

# --- Configuración Principal Corregida ---
config = rx.Config(
    app_name="likemodas",
    
    # ✨ CAMBIO CLAVE AQUÍ ✨
    # Le decimos a Reflex que la URL canónica y pública de la API
    # es tu dominio de producción.
    # ANTES: api_url=RAILWAY_PUBLIC_URL,
    # AHORA:
    api_url=PRODUCTION_DOMAIN,
    
    # La lista de orígenes permitidos está correcta, ya que incluye
    # tanto el dominio de producción como el de Railway y Vercel.
    cors_allowed_origins=[
        "http://localhost:3000",
        RAILWAY_PUBLIC_URL,
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