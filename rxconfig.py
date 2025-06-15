# rxconfig.py
import reflex as rx

# Reflex cargará la configuración directamente de esta clase.
class FullStackPythonConfig(rx.Config):
    app_name = "full_stack_python"
    api_url = "https://page-wpzf.onrender.com" # <-- Tu URL de Render (¡esto está bien!)

    # CORS para tu frontend (¡cambia la URL de Vercel por la real!)
    cors_allowed_origins = [
        "http://localhost:3000",
        # "https://your-vercel-frontend-url.vercel.app", # ¡IMPORTANTE: CAMBIA ESTA POR LA URL REAL DE TU FRONTEND EN VERCEL!
        "http://localhost:8000"
    ]
    
    # Si necesitas db_url, colócala aquí también
    db_url = "sqlite:///reflex.db" 

# ¡Elimina esta línea! Reflex no la necesita y causa conflictos.
# config = rx.Config(
#     app_name="full_stack_python",
#     db_url="sqlite:///reflex.db", 
# )