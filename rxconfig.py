import reflex as rx
import os
from dotenv import load_dotenv

load_dotenv()

# LA VARIABLE DEBE LLAMARSE EXACTAMENTE 'config'
config = rx.Config(
    app_name="likemodas",
    show_built_with_reflex=False,
    
    # Base de datos local (SQLite) para poder exportar sin errores de conexión
    db_url=os.getenv("DATABASE_URL", "sqlite:///reflex.db"),
    
    # URLs locales
    api_url="http://localhost:8000", 
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