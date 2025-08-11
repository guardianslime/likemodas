# rxconfig.py (VERSIÓN FINAL A PRUEBA DE CONFLICTOS)

import reflex as rx
import os

# --- 1. URLs Base ---
API_URL = os.getenv("API_URL", "http://localhost:8000")
DEPLOY_URL = os.getenv("DEPLOY_URL", "https://likemodas.com")
DB_URL = os.getenv(
    "DB_URL",
    "postgresql://postgres:rszvQoEjlvQijlSTROgqCEDPiNdQqqmU@nozomi.proxy.rlwy.net:37918/railway"
)

# --- 2. Lógica Definitiva para CORS ---
# Leemos la variable de entorno de Railway en una variable con un nombre DIFERENTE.
# Esto es CLAVE para evitar que Reflex la lea automáticamente.
# Buscamos tanto en mayúsculas como en minúsculas por si acaso.
raw_cors_str = os.getenv("CORS_ALLOWED_ORIGINS", "") or os.getenv("cors_allowed_origins", "")

# Lista base de orígenes permitidos
allowed_origins = [
    "http://localhost:3000",
    "https://likemodas.com",
    API_URL,
    DEPLOY_URL,
]

# Si la variable de entorno tiene contenido, lo procesamos manualmente.
if raw_cors_str:
    parsed_origins = [origin.strip() for origin in raw_cors_str.split(",")]
    allowed_origins.extend(parsed_origins)

# Aseguramos una lista final limpia y sin duplicados.
final_cors_list = sorted(list(set(allowed_origins)))

# --- 3. Configuración Final ---
config = rx.Config(
    app_name="likemodas",
    api_url=API_URL,
    deploy_url=DEPLOY_URL,
    db_url=DB_URL,
    cors_allowed_origins=final_cors_list,
    disable_plugins=['reflex.plugins.sitemap.SitemapPlugin'],
)