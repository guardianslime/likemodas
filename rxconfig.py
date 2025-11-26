import reflex as rx
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración "blindada"
# Si estamos en local, usa localhost. Si no, usa SIEMPRE tu servidor de producción.
# Esto evita que Vercel se confunda.
api_url = "https://api.likemodas.com" if os.getenv("RAILWAY_ENVIRONMENT_NAME") != "production" else "http://localhost:8000"

# En tu máquina local para desarrollo
if os.environ.get("REFLEX_ENV") == "dev":
    api_url = "http://localhost:8000"

# --- LA LÍNEA DE ORO ---
# Forzamos la URL pública de tu API para que el Frontend sepa a dónde ir.
# Esto sobrescribe cualquier duda que tenga Vercel.
config = rx.Config(
    app_name="likemodas",
    show_built_with_reflex=False,
    
    db_url=os.getenv("DATABASE_URL", "sqlite:///reflex.db"),
    
    # Aquí está la magia: Le decimos explícitamente dónde vive el Backend
    api_url="https://api.likemodas.com",
    
    # Permisos de seguridad (CORS)
    cors_allowed_origins=[
        "http://localhost:3000",
        "https://www.likemodas.com",
        "https://likemodas.com",
        "https://full-stack-python.vercel.app",
    ],
    
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],

    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="medium",
        accent_color="violet",
        panel_background="translucent",
    ),
)
