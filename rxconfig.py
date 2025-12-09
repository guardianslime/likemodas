import reflex as rx
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración para entorno LOCAL
# Cuando ejecutes `reflex run`, usará esto.
config = rx.Config(
    app_name="likemodas",
    show_built_with_reflex=False,
    
    # URL de la base de datos (local o remota, definida en .env)
    db_url=os.getenv("DATABASE_URL", "sqlite:///reflex.db"),
    
    # URL del backend (FastAPI)
    api_url="http://localhost:8000", 
    
    # URL del frontend (Next.js)
    deploy_url="http://localhost:3000",
    
    cors_allowed_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "*"
    ],
    
    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="medium",
        accent_color="violet",
        panel_background="translucent",
    ),
)