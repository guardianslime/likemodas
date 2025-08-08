import os
import reflex as rx

# --- URLs de la aplicación leídas desde el entorno ---
# Prioriza la variable de entorno API_URL. Si no existe, usa la URL de desarrollo local.
# Esto es ideal: Vercel usará la variable que configures, y localmente funcionará sin más.
API_URL = os.getenv("API_URL", "http://localhost:8000")

# La URL pública del frontend. Esencial para los enlaces en correos electrónicos.
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:3000")


# --- Configuración de CORS más robusta ---
default_origins = [
    "http://localhost:3000",
    APP_BASE_URL,
    # Puedes añadir aquí otras URLs estáticas que siempre deban estar permitidas
    # Ejemplo: "https://www.likemodas.com"
]
# Lee orígenes adicionales desde una variable de entorno, separados por comas.
# Esto es útil para las URLs de preview de Vercel.
additional_origins_str = os.getenv("CORS_ALLOWED_ORIGINS", "")
additional_origins = [origin.strip() for origin in additional_origins_str.split(",") if origin.strip()]

cors_allowed_origins = list(set(default_origins + additional_origins))


# --- Configuración Principal de Reflex ---
config = rx.Config(
    app_name="likemodas",
    show_built_with_reflex=False,
    # La URL de la BD puede seguir aquí o también moverse a una variable de entorno.
    db_url="postgresql://postgres:rszvQoEjlvQijlSTROgqCEDPiNdQqqmU@nozomi.proxy.rlwy.net:37918/railway",
    api_url=API_URL,
    cors_allowed_origins=cors_allowed_origins,
    
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
    
    theme=rx.theme(
        appearance="dark",
        has_background=True,
        panel_background="solid",
        radius="medium",
        accent_color="sky"
    ),
)