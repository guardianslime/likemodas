# Dockerfile
FROM python:3.11-slim-buster

# Instala los paquetes 'unzip' y 'curl' requeridos por Reflex
# Además, instala gunicorn y uvicorn para el servidor de producción
RUN apt-get update && apt-get install -y unzip curl && \
    pip install gunicorn uvicorn && \ # AÑADE ESTA LÍNEA para instalar Gunicorn y Uvicorn
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt # Agrega --no-cache-dir para ahorrar espacio

COPY . .

# Elimina 'reflex init' si no es estrictamente necesario en cada build.
# A menudo, reflex init se usa para generar archivos boilerplate o configurar el proyecto localmente.
# Si tu proyecto ya está inicializado y solo necesitas correrlo, esta línea puede no ser necesaria o puede causar problemas.
# RUN reflex init

EXPOSE 8000

# ¡CAMBIO IMPORTANTE EN CMD! Usa Gunicorn para servir tu aplicación Reflex
# "full_stack_python.full_stack_python:app" es la ruta a tu instancia 'app = rx.App()'
# Asegúrate de que esta ruta sea CORRECTA para tu proyecto.
# Si tu app está en 'my_app/my_app.py' y la instancia es 'app', sería 'my_app.my_app:app'
CMD ["gunicorn", "full_stack_python.full_stack_python:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:$PORT"]
