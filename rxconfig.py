# rxconfig.py (SOLUCIÓN DEFINITIVA)

import reflex as rx
import os
from reflex.plugins import SitemapPlugin

# Para desarrollo local, usará "http://localhost:8000".
# En Railway, usará la URL que definas en las variables de entorno.
API_URL = os.getenv("API_URL", "http://localhost:8000")

config = rx.Config(
    app_name="likemodas",
    db_url="postgresql://postgres:rszvQoEjlvQijlSTROgqCEDPiNdQqqmU@nozomi.proxy.rlwy.net:37918/railway",
    api_url=API_URL,
    plugins=[
        SitemapPlugin(),
    ],
)