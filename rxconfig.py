import reflex as rx
import os

# --- URLs de la aplicación (Sin cambios) ---
API_URL = "https://full-stack-python-production.up.railway.app"
DEPLOY_URL = "https://likemodas.com"
PREVIEW_URL = "https://full-stack-python-ibehoa7sb-nkpz01s-projects.vercel.app"
VERCEL_LEGACY_URL = "https://full-stack-python.vercel.app"


# --- Lista de orígenes permitidos por defecto (Sin cambios) ---
default_origins = [
    "http://localhost:3000",
    API_URL,
    DEPLOY_URL,
    "https://www.likemodas.com",
    PREVIEW_URL,
    VERCEL_LEGACY_URL,
]

additional_origins = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
cors_allowed_origins = list(
    {
        origen.strip()
        for origen in default_origins + additional_origins
        if origen.strip()
    }
)

# --- Configuración Principal con el Tema Añadido ---
config = rx.Config(
    app_name="likemodas",
    show_built_with_reflex=False,
    db_url="postgresql://postgres:rszvQoEjlvQijlSTROgqCEDPiNdQqqmU@nozomi.proxy.rlwy.net:37918/railway",
    api_url=API_URL,
    cors_allowed_origins=cors_allowed_origins,
    
    # ▼▼▼ ESTA ES LA ÚNICA SECCIÓN AÑADIDA ▼▼▼
    # Unifica la definición del tema en un solo lugar.
    theme=rx.theme(
        appearance="dark",
        has_background=True,
        panel_background="solid",
        radius="medium",
        accent_color="sky"
    ),
)