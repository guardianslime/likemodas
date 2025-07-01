import reflex as rx
import os

# --- URLs de Producción ---

# Para el backend (en Railway), leemos la URL del frontend.
# Valor por defecto para desarrollo local.
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Para el frontend (en Vercel), leemos la URL del backend.
# ¡Ahora buscamos "API_URL", que coincide con la variable en Vercel!
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


class FullStackPythonConfig(rx.Config):
    # El nombre de tu app. Cámbialo si tu carpeta principal se llama diferente.
    app_name = "simple_app" 
    
    # Configura las URLs usando las variables leídas arriba.
    api_url: str = API_URL
    deploy_url: str = FRONTEND_URL
    
    # Lista de orígenes permitidos para CORS.
    # Esto permite que tu frontend en Vercel se conecte al backend.
    cors_allowed_origins: list[str] = [
        "http://localhost:3000",
        FRONTEND_URL,
    ]
    
    # Configuración de la base de datos.
    db_url: str = os.getenv("DATABASE_URL", "sqlite:///reflex.db")

config = FullStackPythonConfig()
