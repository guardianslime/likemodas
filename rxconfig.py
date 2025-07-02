# rxconfig.py
import reflex as rx
import os



# Lee la lista de orígenes desde una variable de entorno, con valores por defecto
cors_allowed_origins_str = os.getenv(
    "CORS_ALLOWED_ORIGINS", 
    "http://localhost:3000,https://full-stack-python.vercel.app"
)
allowed_origins = [origin.strip() for origin in cors_allowed_origins_str.split(",")]

config = rx.Config(
    app_name="full_stack_python",
    
    # 👇 USA LA VARIABLE DE ENTORNO PARA LA BASE DE DATOS
    # En Railway, usará la URL de la base de datos de producción automáticamente.
    # En tu PC, usará una base de datos local si no defines la variable.
    db_url=os.getenv("DATABASE_URL", "sqlite:///reflex.db"),
    
    cors_allowed_origins=allowed_origins,
)
