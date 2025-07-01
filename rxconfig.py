import reflex as rx

config = rx.Config(
    app_name="nombre_de_tu_app",
    api_url="https://web-production-50b7a.up.railway.app",  # Usa la URL pública de Railway con el puerto 8000
    deploy_url="https://full-stack-python.vercel.appp",     # URL pública de tu frontend en Vercel
    cors_allowed_origins=["https://full-stack-python.vercel.app"],  # Permite que el frontend acceda al backend
)