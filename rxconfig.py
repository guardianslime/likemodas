# likemodas/rxconfig.py (SOLUCIÓN DEFINITIVA)

import reflex as rx
import os
from reflex.plugins import SitemapPlugin

# --- URLs (Conservamos tu estructura) ---
API_URL_PROD = "https://full-stack-python-production.up.railway.app"
DEPLOY_URL = "https://likemodas.com"
PREVIEW_URL = "https://full-stack-python-ibehoa7sb-nkpz01s-projects.vercel.app"
VERCEL_LEGACY_URL = "https://full-stack-python.vercel.app"

# ✨ EXPLICACIÓN: Esta es la línea clave.
# Usará la URL de producción por defecto, pero si estás corriendo
# localmente, puedes crear un archivo `.env` para sobreescribirla.
API_URL = os.getenv("API_URL", API_URL_PROD)

# --- CORS (Conservamos tu estructura) ---
default_origins = [
    "http://localhost:3000",
    API_URL,
    DEPLOY_URL,
    "https://www.likemodas.com",
    PREVIEW_URL,
    VERCEL_LEGACY_URL,
]
cors_allowed_origins = list(
    {
        origen.strip()
        for origen in default_origins + os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
        if origen.strip()
    }
)

# --- Configuración Principal ---
config = rx.Config(
    app_name="likemodas",
    db_url="postgresql://postgres:rszvQoEjlvQijlSTROgqCEDPiNdQqqmU@nozomi.proxy.rlwy.net:37918/railway",
    api_url=API_URL,
    cors_allowed_origins=cors_allowed_origins,
    plugins=[
        SitemapPlugin(),
    ],
)