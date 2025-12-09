import reflex as rx
import os
from dotenv import load_dotenv

load_dotenv()

config = rx.Config(
    app_name="likemodas",
    show_built_with_reflex=False,
    
    # Base de datos (Leerá SQLite del .env para poder exportar)
    db_url=os.getenv("DATABASE_URL"),
    
    # URLs (Leerá https://www.likemodas.com del .env para conectar Vercel con Hetzner)
    api_url=os.getenv("API_URL"),
    deploy_url=os.getenv("DEPLOY_URL"),
    
    cors_allowed_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
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