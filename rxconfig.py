# rxconfig.py (VERSIÓN SIMPLIFICADA Y DEFINITIVA)

import reflex as rx
import os

# Lee las variables de entorno que sabemos que funcionan.
# Si no existen (en local), usa valores de respaldo seguros.
API_URL = os.getenv("API_URL", "http://localhost:8000")
DEPLOY_URL = os.getenv("DEPLOY_URL", "https://likemodas.com")
DB_URL = os.getenv(
    "DB_URL",
    "postgresql://postgres:rszvQoEjlvQijlSTROgqCEDPiNdQqqmU@nozomi.proxy.rlwy.net:37918/railway"
)

# --- Creamos la configuración SIN el parámetro conflictivo ---
config = rx.Config(
    app_name="likemodas",
    api_url=API_URL,
    deploy_url=DEPLOY_URL,
    db_url=DB_URL,
    # Se ha eliminado por completo la línea 'cors_allowed_origins'
)