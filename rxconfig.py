import reflex as rx
import os

# --- LECTURA DE VARIABLES DE ENTORNO ---
# Lee la URL del frontend (para CORS en el backend). Usa un valor por defecto para desarrollo local.
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Lee la URL del backend (para que el frontend sepa a dónde conectar). Usa un valor por defecto para desarrollo local.
# ¡IMPORTANTE! Lee "API_URL", que es el nombre de la variable que configuraste en Vercel.
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


class FullStackPythonConfig(rx.Config):
    # Asegúrate de que este nombre coincida con el de la carpeta principal de tu código.
    # Si tu código está en 'simple_app/simple_app.py', debería ser "simple_app".
    # Si está en 'full_stack_python/full_stack_python.py', es "full_stack_python".
    app_name = "simple_app" 
    
    # Configura las URLs usando las variables leídas arriba.
    api_url: str = API_URL
    deploy_url: str = FRONTEND_URL
    
    # Lista de orígenes permitidos para CORS.
    # Esto es crucial para que tu backend en Railway acepte la conexión de Vercel.
    cors_allowed_origins: list[str] = [
        FRONTEND_URL,
        "http://localhost:3000",
    ]
    
    # Configuración de la base de datos.
    db_url: str = os.getenv("DATABASE_URL", "sqlite:///reflex.db")

config = FullStackPythonConfig()