# Dockerfile
# Usa una imagen base de Python (reflex recomienda slim)
FROM python:3.11-slim-buster

# Instala paquetes de sistema requeridos (unzip, curl)
RUN apt-get update && apt-get install -y unzip curl

# Instala los servidores de producción Gunicorn y Uvicorn
RUN pip install gunicorn uvicorn

# Limpia el caché de APT para reducir el tamaño de la imagen
RUN rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos de requisitos e instala las dependencias de tu proyecto
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el contenido de tu proyecto local al directorio de trabajo en el contenedor
# Esto incluye tu carpeta 'full_stack_python/', 'rxconfig.py', etc.
COPY . .

# Expone el puerto que tu aplicación escuchará
EXPOSE 8000

# Comando para ejecutar la aplicación con Gunicorn y Uvicorn
# La clave aquí es la ruta "full_stack_python.full_stack_python:app"
# Asegúrate de que esta ruta apunte DIRECTAMENTE a la instancia 'app = rx.App()'
# Si tu app principal está en `full_stack_python/full_stack_python.py` y tu instancia se llama `app`,
# entonces esta ruta es correcta. Si se llama `main.py` o tiene otro nombre de carpeta, ajusta.
#
# Hemos hardcodeado el puerto a 8000 en el CMD para pruebas, como lo solicitaste.
# Si Render te sigue dando errores de puerto con $PORT, esta es una buena prueba.
CMD ["gunicorn", "full_stack_python.full_stack_python:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
