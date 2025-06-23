import reflex as rx
import os
from typing import List, Optional, Dict, Any

# --- URLs de Producción ---
# La URL donde vivirá tu backend (Railway)
BACKEND_PRODUCTION_URL = "https://web-production-15ad.up.railway.app"
# La URL donde vivirá tu frontend (Vercel) - ¡CAMBIA ESTO!
FRONTEND_PRODUCTION_URL = "https://tu-proyecto.vercel.app" 


class FullStackPythonConfig(rx.Config):
    app_name = "full_stack_python"
    telemetry_enabled = False
    frontend_port = 3000
    backend_port = 8000
    
    # La URL del API a la que el frontend se conectará.
    api_url: str = os.getenv("API_URL", f"http://127.0.0.1:{backend_port}")

    # La URL pública del frontend.
    deploy_url: str = os.getenv("FRONTEND_URL", f"http://localhost:{frontend_port}")

    # ¡LA PARTE MÁS IMPORTANTE PARA ESTE CASO!
    # El CORS debe permitir tu PC, Railway, y AHORA TAMBIÉN VERCEL.
    cors_allowed_origins: List[str] = [
        f"http://localhost:{frontend_port}",  # Para desarrollo local
        BACKEND_PRODUCTION_URL,              # Para el propio backend
        FRONTEND_PRODUCTION_URL,             # ¡Para tu frontend en Vercel!
    ]
    
    db_url: str = os.getenv("DATABASE_URL", "sqlite:///reflex.db")
    tailwind: Optional[Dict[str, Any]] = None

config = FullStackPythonConfig()