import reflex as rx
import os

# --- URLs de la aplicación ---
# URL del backend donde corre la API de Reflex
API_URL = "https://full-stack-python-production.up.railway.app"

# URL principal del frontend desplegado en Vercel
DEPLOY_URL = "https://likemodas.com"

# URL de preview que causaba el error
PREVIEW_URL = "https://full-stack-python-ibehoa7sb-nkpz01s-projects.vercel.app"


# --- Lista de orígenes permitidos por defecto ---
# Incluye localhost, la URL de la API y las URLs de Vercel
default_origins = [
    "http://localhost:3000",
    API_URL,
    DEPLOY_URL,  # <-- Ahora es https://likemodas.com
    "https://www.likemodas.com",  # ✨ AÑADIDO: La versión 'www' es crucial
    PREVIEW_URL,
]

# Lee orígenes adicionales desde las variables de entorno, si existen
additional_origins = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")

# Combina y limpia la lista final de orígenes
# Se eliminan espacios en blanco y entradas vacías
cors_allowed_origins = list(
    {
        origen.strip()
        for origen in default_origins + additional_origins
        if origen.strip()
    }
)


config = rx.Config(
    app_name="Likemodas",
    show_built_with_reflex=False,
    db_url="postgresql://postgres:rszvQoEjlvQijlSTROgqCEDPiNdQqqmU@nozomi.proxy.rlwy.net:37918/railway",
    api_url=API_URL,
    cors_allowed_origins=cors_allowed_origins,
)
