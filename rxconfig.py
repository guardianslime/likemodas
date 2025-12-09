import reflex as rx
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración
# Si no encuentra la variable (ej. en producción automática), usa la de producción por defecto
api_url = os.getenv("API_URL", "https://api.likemodas.com")
deploy_url = os.getenv("DEPLOY_URL", "https://www.likemodas.com")

config = rx.Config(
    app_name="likemodas",
    show_built_with_reflex=False,
    
    # Base de datos
    db_url=os.getenv("DATABASE_URL"),
    
    # URLs de conexión
    api_url=api_url,
    deploy_url=deploy_url,
    
    cors_allowed_origins=[
        "http://localhost:3000",
        "https://www.likemodas.com",
        "https://likemodas.com",
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