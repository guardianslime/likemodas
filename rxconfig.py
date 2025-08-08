import reflex as rx
import os

# La URL pública donde vivirá tu aplicación en Railway.
# Esta es la única URL que necesitamos.
RAILWAY_PUBLIC_URL = "https://full-stack-python-production.up.railway.app"

# La URL final para tus usuarios.
PRODUCTION_DOMAIN = "https://www.likemodas.com"

# --- Configuración Principal Simplificada ---
config = rx.Config(
    app_name="likemodas",
    
    # Reflex necesita saber su propia URL pública para funcionar correctamente.
    api_url=RAILWAY_PUBLIC_URL,
    
    # Lista blanca de dominios permitidos para conectarse.
    cors_allowed_origins=[
        RAILWAY_PUBLIC_URL,
        PRODUCTION_DOMAIN,
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