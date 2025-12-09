import reflex as rx
import os
from dotenv import load_dotenv

load_dotenv()

config = rx.Config(
    app_name="likemodas",
    show_built_with_reflex=False,
    
    # Base de datos: Obedece ciegamente a la variable de entorno
    db_url=os.getenv("DATABASE_URL"),
    
    # URLs: Obedecen ciegamente a las variables de entorno
    # Si no existen (en local sin .env cargado), usa localhost por defecto
    api_url=os.getenv("API_URL", "http://localhost:8000"),
    deploy_url=os.getenv("DEPLOY_URL", "http://localhost:3000"),
    
    cors_allowed_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "https://www.likemodas.com",
        "https://likemodas.com",
        "https://www.likemodas.com/returns",
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