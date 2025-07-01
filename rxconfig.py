import reflex as rx
import os

# --- CLASE DE CONFIGURACIÓN (simple) ---
class FullStackPythonConfig(rx.Config):
    pass

# --- URLs DE PRODUCCIÓN DEFINIDAS MANUALMENTE ---
# Aquí ponemos tus URLs directamente para que no haya dudas.
FRONTEND_URL_PROD = "https://full-stack-python-1dqv.vercel.app"
API_URL_PROD = "https://web-production-50b7a.up.railway.app"

# --- CREACIÓN DE LA CONFIGURACIÓN ---
# Creamos la instancia de la configuración pasando los valores directamente.
# Este método es explícito y elimina cualquier ambigüedad.
config = FullStackPythonConfig(
    # Asegúrate de que este nombre coincida con tu carpeta de código principal.
    app_name="full_stack_python",
    
    # Asignamos las URLs directamente.
    api_url=API_URL_PROD,
    deploy_url=FRONTEND_URL_PROD,
    
    # La lista de orígenes permitidos para CORS.
    cors_allowed_origins=[
        FRONTEND_URL_PROD,
        "http://localhost:3000",
    ],
    
    # La URL de la base de datos SÍ debe usar os.getenv,
    # ya que Railway la inyecta de forma segura y garantizada.
    db_url=os.getenv("DATABASE_URL", "sqlite:///reflex.db"),
)
