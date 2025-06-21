# rxconfig.py
import reflex as rx
import os
from typing import List

# La variable de entorno RAILWAY_PUBLIC_DOMAIN ya no es estrictamente necesaria
# para la api_url si Caddy se encarga del proxying en el mismo servicio,
# pero se mantiene para consistencia si en el futuro decides revertir o usarla de otra forma.
RAILWAY_PUBLIC_DOMAIN_VAR = "RAILWAY_PUBLIC_DOMAIN" 

class FullStackPythonConfig(rx.Config):
    """Clase de configuración para tu aplicación Reflex."""

    app_name = "full_stack_python"  # ¡Mantén el nombre de tu app!
    telemetry_enabled = False       # O True
    frontend_port = 3000            # Puertos por defecto (para desarrollo local)
    backend_port = 8000

    # api_url ahora es una ruta RELATIVA, ya que Caddy en el mismo servicio hará el proxy.
    api_url: str = "/backend" 

    # CORS: si frontend y backend están en el mismo dominio, CORS se relaja.
    # Pero para desarrollo local, aún necesitas los orígenes de localhost.
    cors_allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000"
        # Ya no es necesaria la URL de Vercel aquí si el frontend se sirve desde Railway.
    ]
    
    db_url = "sqlite:///reflex.db"

config = FullStackPythonConfig()
