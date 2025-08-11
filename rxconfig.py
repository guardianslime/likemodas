import reflex as rx
import os

# --- Configuración Definitiva para Reflex 0.7.0 en Railway ---

# 1. Obtener la URL base de la API desde las variables de entorno de Railway.
#    Si no existe, se usa la URL de desarrollo local.
API_URL = os.getenv("RAILWAY_PUBLIC_URL", "http://localhost:8000")

# 2. Leer los orígenes CORS desde la variable de entorno. Railway las pasa como un string separado por comas.
cors_env = os.getenv("CORS_ALLOWED_ORIGINS", "")
if cors_env:
    # Si la variable de entorno existe, la separamos por comas para crear la lista.
    CORS_ALLOWED_ORIGINS = [origin.strip() for origin in cors_env.split(",")]
else:
    # Si no, usamos una lista segura para desarrollo local.
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "https://full-stack-python.vercel.app",
        "https://www.likemodas.com",
    ]

# 3. Nos aseguramos de que la propia URL de la API esté en la lista.
if API_URL not in CORS_ALLOWED_ORIGINS:
    CORS_ALLOWED_ORIGINS.append(API_URL)

# 4. Creamos el objeto de configuración.
config = rx.Config(
    app_name="likemodas",
    api_url=API_URL,
    db_url="postgresql://postgres:rszvQoEjlvQijlSTROgqCEDPiNdQqqmU@nozomi.proxy.rlwy.net:37918/railway",
    cors_allowed_origins=CORS_ALLOWED_ORIGINS,
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"], # <-- AÑADE ESTA LÍNEA
)