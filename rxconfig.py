import reflex as rx
import os

# --- Configuración Principal Corregida para Reflex 0.7.0 ---

# Las URLs se obtienen de las variables de entorno que Railway proporciona.
API_URL = os.getenv("RAILWAY_PUBLIC_URL", "http://localhost:8000")
DEPLOY_URL = os.getenv("DEPLOY_URL", "http://localhost:3000")

# Lista de orígenes permitidos
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://full-stack-python.vercel.app", # Tu URL de Vercel
    "https://www.likemodas.com", # Tu dominio de producción
]

# Si la URL de Railway está presente, la añadimos dinámicamente.
if "railway.app" in API_URL:
    CORS_ALLOWED_ORIGINS.append(API_URL)


config = rx.Config(
    app_name="likemodas",
    api_url=API_URL,
    deploy_url=DEPLOY_URL,
    db_url="postgresql://postgres:rszvQoEjlvQijlSTROgqCEDPiNdQqqmU@nozomi.proxy.rlwy.net:37918/railway",
    cors_allowed_origins=CORS_ALLOWED_ORIGINS,
    
    # El telemetría es opcional, pero es buena práctica gestionarlo.
    # telemetry_enabled=False, 
)