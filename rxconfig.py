import reflex as rx
import os
from dotenv import load_dotenv

load_dotenv()

config = rx.Config(
    app_name="likemodas",
    show_built_with_reflex=False,
    
    # Lee la base de datos de la variable (Local en tu PC, Postgres en Hetzner)
    db_url=os.getenv("DATABASE_URL"),
    
    # Lee las URLs de la variable (Siempre https://www.likemodas.com en esta config)
    api_url=os.getenv("API_URL"),
    deploy_url=os.getenv("DEPLOY_URL"),
    
    # --- LISTA DE CORS ACTUALIZADA ---
    # Esto permite que Vercel se conecte a Hetzner sin bloqueos
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