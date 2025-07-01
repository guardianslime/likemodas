import reflex as rx
import os

class SimpleappConfig(rx.Config):
    app_name: str = "simple_app"
    
    # La URL del backend que Railway te dará.
    # Lee desde una variable de entorno en producción.
    api_url: str = os.getenv("API_URL", "http://127.0.0.1:8000")

config = SimpleappConfig()
