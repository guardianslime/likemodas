# likemodas/rxconfig.py

import reflex as rx
import os
from reflex.plugins import SitemapPlugin

# Para desarrollo local, usará "http://localhost:8000".
# En Railway, usará la URL que definas en las variables de entorno.
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Reintroducimos tu configuración original de CORS para máxima compatibilidad
default_origins = [
    "http://localhost:3000",
    "https://full-stack-python-production.up.railway.app",
    "https://likemodas.com",
    "https://www.likemodas.com",
    "https://full-stack-python-ibehoa7sb-nkpz01s-projects.vercel.app",
    "https://full-stack-python.vercel.app",
]
additional_origins = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
cors_allowed_origins = list(
    {
        origen.strip()
        for origen in default_origins + additional_origins
        if origen.strip()
    }
)

config = rx.Config(
    app_name="likemodas",
    db_url="postgresql://postgres:rszvQoEjlvQijlSTROgqCEDPiNdQqqmU@nozomi.proxy.rlwy.net:37918/railway",
    api_url=API_URL,
    cors_allowed_origins=cors_allowed_origins,
    plugins=[
        SitemapPlugin(),
    ],
)