# rxconfig.py

import reflex as rx
import os
from typing import List

# --- URLs de Producción Corregidas y Centralizadas ---
# La URL pública donde vivirá el backend (Railway)
# Asegúrese de que esta sea la URL que Railway le proporciona.
BACKEND_PRODUCTION_URL = "https://web-production-15ad.up.railway.app"

# La URL pública donde vivirá el frontend (Vercel)
# ¡CORREGIDO! Se ha eliminado el error tipográfico "vercele".
FRONTEND_PRODUCTION_URL = "https://mi-frontend-vercel.vercel.app" 

class FullStackPythonConfig(rx.Config):
    app_name = "full_stack_python"
    telemetry_enabled = False
    frontend_port = 3000
    backend_port = 8000
    
    # Este patrón es excelente. Utiliza la variable de entorno API_URL cuando está disponible (en producción)
    # y recurre a la URL local para el desarrollo.
    api_url: str = os.getenv("API_URL", f"http://127.0.0.1:{backend_port}")

    # Este patrón también es correcto para la URL de despliegue del frontend.
    deploy_url: str = os.getenv("FRONTEND_URL", f"http://localhost:{frontend_port}")

    # ¡CORREGIDO! La lista de orígenes CORS ahora solo incluye los orígenes del frontend.
    # Esto es más seguro y conceptualmente correcto. El backend no necesita incluirse a sí mismo.
    cors_allowed_origins: List[str] =
    
    # La configuración de la base de datos es correcta. Railway proporcionará la URL a través de DATABASE_URL.
    db_url: str = os.getenv("DATABASE_URL", "sqlite:///reflex.db")

config = FullStackPythonConfig()
