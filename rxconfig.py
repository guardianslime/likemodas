import reflex as rx
import os

# --- URLs de Producción ---
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://full-stack-python-1dqv.vercel.app")
API_URL = os.getenv("API_URL", "https://web-production-50b7a.up.railway.app")

class FullStackPythonConfig(rx.Config):
    app_name = "full_stack_python"
    
    api_url: str = API_URL
    deploy_url: str = FRONTEND_URL
    
    cors_allowed_origins: list[str] = [
        "http://localhost:3000",
        FRONTEND_URL,
    ]
    
    db_url: str = os.getenv("DATABASE_URL", "sqlite:///reflex.db")

    # --- CORRECCIÓN CLAVE ---
    # Le decimos a Reflex que la ruta para los WebSockets no debe incluir
    # el subdirectorio _event, lo que a menudo soluciona problemas con proxies.
    socket: str = f"{API_URL.replace('https:', '')}"

config = FullStackPythonConfig()
