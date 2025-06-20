# Dockerfile
# Usa una imagen base de Python (reflex recomienda slim)
FROM python:3.11-slim-buster

# --- INICIO DE CAMBIOS PARA RESOLVER EL ERROR "Bun or npm not found" ---
# Instala Node.js, npm, build-essential y git.
# Node.js y npm son requeridos por Reflex internamente para compilar el frontend,
# incluso en el backend. build-essential proporciona herramientas de compilación.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    nodejs \
    npm \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*
# --- FIN DE CAMBIOS ---

# Instala los servidores de producción Gunicorn y Uvicorn
RUN pip install gunicorn uvicorn

# Limpia el caché de APT para reducir el tamaño de la imagen
# Esto es una buena práctica para mantener las imágenes de Docker más pequeñas
RUN rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos de requisitos e instala las dependencias de tu proyecto
# Asegúrate de que 'requirements.txt' esté en la misma carpeta que este Dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el contenido de tu proyecto local al directorio de trabajo en el contenedor
# Esto incluye tu carpeta 'full_stack_python/', 'rxconfig.py', etc.
COPY . .

# Expone el puerto que tu aplicación escuchará
# Railway detectará esto automáticamente.
EXPOSE 8000

# Comando para ejecutar la aplicación con Gunicorn y Uvicorn
# La clave aquí es la ruta "full_stack_python.full_stack_python:app"
# Asegúrate de que esta ruta apunte DIRECTAMENTE a la instancia 'app = rx.App()'
# Si tu app principal está en `full_stack_python/full_stack_python.py` y tu instancia se llama `app`,
# entonces esta ruta es correcta. Si se llama `main.py` o tiene otro nombre de carpeta, ajusta.
#
# Hemos añadido `--timeout 120` para darle más tiempo al worker a arrancar,
# lo cual puede ser necesario si la compilación interna de Reflex es lenta.
CMD ["gunicorn", "full_stack_python.full_stack_python:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120"]
