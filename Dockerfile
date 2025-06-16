# Dockerfile
FROM python:3.11-slim-buster

# Instala paquetes de sistema y herramientas
# Esta es la primera instrucción RUN, para apt-get y unzip/curl
RUN apt-get update && apt-get install -y unzip curl

# Instala gunicorn y uvicorn con pip
# Esta es la segunda instrucción RUN, solo para pip
RUN pip install gunicorn uvicorn

# Limpia el caché de APT (ahora en su propia instrucción RUN para evitar errores)
# Esta es la tercera instrucción RUN, que antes era la problemática línea 8
RUN rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Si no es absolutamente necesario, comenta o elimina esta línea para producción:
# RUN reflex init

EXPOSE 8000

# Comando para ejecutar la aplicación con Gunicorn y Uvicorn
# "full_stack_python.full_stack_python:app" es la ruta a tu instancia 'app = rx.App()'
# Asegúrate de que esta ruta sea CORRECTA para tu proyecto.
CMD ["gunicorn", "full_stack_python.full_stack_python:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:$PORT"]
