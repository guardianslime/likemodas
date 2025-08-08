import reflex as rx
import os

# La URL pública donde vivirá tu aplicación en Railway.
RAILWAY_PUBLIC_URL = "https://full-stack-python-production.up.railway.app"

# La URL final para tus usuarios.
PRODUCTION_DOMAIN = "https://www.likemodas.com"

# La URL de Vercel que estaba causando el error de CORS.
VERCEL_PREVIEW_URL = "https://full-stack-python.vercel.app"

# --- Configuración Principal Corregida ---
config = rx.Config(
    app_name="likemodas",
    
    # Reflex necesita saber su propia URL pública para funcionar correctamente.
    api_url=RAILWAY_PUBLIC_URL,
    
    # Lista blanca de dominios permitidos para conectarse.
    # Se añaden la URL de Vercel y la de desarrollo local.
    cors_allowed_origins=[
        "http://localhost:3000", # Para desarrollo local
        RAILWAY_PUBLIC_URL,
        PRODUCTION_DOMAIN,
        VERCEL_PREVIEW_URL,
    ],
    
    db_url="postgresql://postgres:rszvQoEjlvQijlSTROgqCEDPiNdQqqmU@nozomi.proxy.rlwy.net:37918/railway",
    
    # Desactivamos el plugin de sitemap que daba problemas en algunas versiones.
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
    
    # Definimos el tema aquí para mantener todo en un solo lugar.
    theme=rx.theme(
        appearance="dark",
        has_background=True,
        panel_background="solid",
        radius="medium",
        accent_color="sky"
    ),
)