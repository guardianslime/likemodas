# rxconfig.py (VERSIÓN FINAL Y ROBUSTA)

import reflex as rx
import os

# --- 1. Obtener la URL de la base de datos de forma segura ---
# Usamos la variable de entorno de Railway, pero si no existe (en local),
# usamos la URL de conexión directa como respaldo.
DB_URL = os.getenv(
    "DB_URL",
    "postgresql://postgres:rszvQoEjlvQijlSTROgqCEDPiNdQqqmU@nozomi.proxy.rlwy.net:37918/railway"
)

# --- 2. Obtener las URLs de la API y del despliegue ---
# Railway las inyecta automáticamente, pero definimos valores locales por si acaso.
API_URL = os.getenv("API_URL", "http://localhost:8000")
DEPLOY_URL = os.getenv("DEPLOY_URL", "https://likemodas.com")

# --- 3. Procesar los orígenes CORS ---
# Esta lógica ya es robusta y la mantenemos.
cors_env_str = os.getenv("cors_allowed_origins", "")
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://likemodas.com",
    "https://full-stack-python.vercel.app",
    API_URL,
    DEPLOY_URL,
]
if cors_env_str:
    parsed_origins = [origin.strip() for origin in cors_env_str.split(",")]
    CORS_ALLOWED_ORIGINS.extend(parsed_origins)

final_cors_list = sorted(list(set(CORS_ALLOWED_ORIGINS)))

# --- 4. Crear la configuración final ---
config = rx.Config(
    app_name="likemodas",
    api_url=API_URL,
    deploy_url=DEPLOY_URL,
    db_url=DB_URL,  # Usamos nuestra variable segura
    cors_allowed_origins=final_cors_list,
    
    # --- BONUS: Desactivar el plugin para eliminar el warning ---
    disable_plugins=['reflex.plugins.sitemap.SitemapPlugin'],
)