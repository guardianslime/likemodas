import reflex as rx
import os

# --- URLs DE PRODUCCIÓN DEFINIDAS MANUALMENTE ---
# Ignoramos las variables de entorno y usamos los valores directamente.
# Esta es la URL de tu frontend en Vercel.
FRONTEND_URL_PROD = "https://full-stack-python.vercel.app"

# Esta es la URL de tu backend en Railway.
API_URL_PROD = "https://web-production-50b7a.up.railway.app"


class FullStackPythonConfig(rx.Config):
    # Asegúrate de que este nombre coincida con tu carpeta de código principal.
    app_name = "full_stack_python"
    
    # --- CONFIGURACIÓN CLAVE ---
    # Asignamos las URLs directamente.
    api_url: str = API_URL_PROD
    deploy_url: str = FRONTEND_URL_PROD
    
    # La lista de orígenes permitidos para CORS.
    # Al definir la URL de Vercel aquí, el backend la aceptará.
    cors_allowed_origins: list[str] = [
        FRONTEND_URL_PROD,
        "http://localhost:3000",
    ]
    
    # La URL de la base de datos SÍ debe usar os.getenv,
    # ya que Railway la inyecta de forma segura y garantizada.
    db_url: str = os.getenv("DATABASE_URL", "sqlite:///reflex.db")

config = FullStackPythonConfig()