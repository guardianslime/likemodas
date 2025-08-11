# /app/rxconfig.py (VERSIÓN DEFINITIVA Y A PRUEBA DE ERRORES)

import reflex as rx
import os

# --- 1. Obtener las URLs base de las variables de entorno ---
# Si no existen, usamos valores por defecto para el desarrollo local.
API_URL = os.getenv("API_URL", "http://localhost:8000")
DEPLOY_URL = os.getenv("DEPLOY_URL", "http://localhost:3000")

# --- 2. Lógica robusta para procesar CORS ---
# Leemos la variable de entorno CORS_ALLOWED_ORIGINS como un simple string.
cors_env_str = os.getenv("cors_allowed_origins", "")

# Creamos nuestra lista base de orígenes permitidos.
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://likemodas.com",
    "https://full-stack-python.vercel.app",
    API_URL,
    DEPLOY_URL,
]

# Si Railway nos pasó un string con orígenes, lo procesamos.
if cors_env_str:
    # Separamos el string por comas y limpiamos los espacios.
    # Esto convierte "url1, url2, url3" en ["url1", "url2", "url3"]
    parsed_origins = [origin.strip() for origin in cors_env_str.split(",")]
    # Añadimos los orígenes parseados a nuestra lista principal.
    CORS_ALLOWED_ORIGINS.extend(parsed_origins)

# --- 3. Eliminamos duplicados y creamos la configuración ---
# Usamos set() para asegurar que no haya URLs repetidas.
final_cors_list = sorted(list(set(CORS_ALLOWED_ORIGINS)))

config = rx.Config(
    app_name="likemodas",
    api_url=API_URL,
    deploy_url=DEPLOY_URL,
    db_url=os.getenv("DB_URL"), # Es mejor leerla siempre del entorno por seguridad
    cors_allowed_origins=final_cors_list,
)