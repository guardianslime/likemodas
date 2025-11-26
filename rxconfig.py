import reflex as rx
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración
api_url = "https://api.likemodas.com"

config = rx.Config(
    app_name="likemodas",
    show_built_with_reflex=False,
    
    db_url=os.getenv("DATABASE_URL", "sqlite:///reflex.db"),
    
    api_url=api_url,
    deploy_url="https://www.likemodas.com",
    
    cors_allowed_origins=[
        "*"
    ],
    
    # --- ¡LÍNEA BORRADA AQUÍ! ---
    # Ya no desactivamos el sitemap.
    
    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="medium",
        accent_color="violet",
        panel_background="translucent",
    ),
)