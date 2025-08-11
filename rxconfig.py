# rxconfig.py (VERSIÓN FINAL Y DEFINITIVA)

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
# Leemos nuestra variable de entorno personalizada y no conflictiva.
raw_cors_str = os.getenv("MY_CORS_URLS", "")

# Lista base de orígenes permitidos
allowed_origins = [
    "http://localhost:3000",
    "https://likemodas.com",
    API_URL,
    DEPLOY_URL,
]

if raw_cors_str:
    parsed_origins = [origin.strip() for origin in raw_cors_str.split(",")]
    allowed_origins.extend(parsed_origins)

final_cors_list = sorted(list(set(allowed_origins)))

# --- 3. Configuración Final ---
# El parámetro cors_allowed_origins se vuelve a añadir, ya que ahora es seguro.
config = rx.Config(
    app_name="likemodas",
    api_url=API_URL,
    deploy_url=DEPLOY_URL,
    db_url=DB_URL,
    cors_allowed_origins=final_cors_list,
    disable_plugins=['reflex.plugins.sitemap.SitemapPlugin'],
)