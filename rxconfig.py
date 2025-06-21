# rxconfig.py
import reflex as rx
import os
from typing import List

# Define el nombre de la variable de entorno que Railway usará para tu dominio público.
RAILWAY_PUBLIC_DOMAIN_VAR = "RAILWAY_PUBLIC_DOMAIN" 

class FullStackPythonConfig(rx.Config):
    # ATRIBUTOS DE CLASE:
    # Estos son parte de la configuración por defecto de tu aplicación.
    app_name = "full_stack_python" 
    telemetry_enabled = False # O True si quieres enviar telemetría a Reflex
    frontend_port = 3000      # Puerto por defecto de tu frontend local
    backend_port = 8000       # Puerto por defecto de tu backend local

    # Tus orígenes CORS permitidos.
    # ¡IMPORTANTE! Asegúrate de que la URL de Vercel sea la EXACTA y SIN BARRA FINAL.
    cors_allowed_origins: List[str] = [
        "http://localhost:3000", # Para desarrollo local
        "https://frontend-snowy-six-69.vercel.app", # <--- ¡TU URL ACTUAL DE VERCEL SIN BARRA FINAL!
        "http://localhost:8000"  # A veces necesario para el backend local
    ]
    
    db_url = "sqlite:///reflex.db" # Si estás usando SQLite

    # LÓGICA PARA api_url:
    # Este es el único atributo que se calcula dinámicamente y se pasa al constructor de rx.Config
    # porque su valor depende de una variable de entorno.
    # Si la variable de entorno RAILWAY_PUBLIC_DOMAIN_VAR existe (en Railway),
    # usa la URL de Railway con HTTPS y la ruta '/backend'.
    # De lo contrario (localmente), usa la dirección local.
    api_url = (
        f'https://{os.environ[RAILWAY_PUBLIC_DOMAIN_VAR]}/backend' 
        if RAILWAY_PUBLIC_DOMAIN_VAR in os.environ 
        else "http://127.0.0.1:8000"
    )

# Crea la instancia de configuración usando la clase definida
config = FullStackPythonConfig()
