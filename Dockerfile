# Dockerfile para el Backend en Railway (Versión Simplificada)

FROM python:3.11-slim

# Permite a pip instalar paquetes
ENV PIP_BREAK_SYSTEM_PACKAGES=1
WORKDIR /app

# Instala dependencias del sistema necesarias para compilar algunas librerías
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

# Copia e instala las dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el código de la aplicación
COPY . .

# Expone el puerto que usará Reflex
EXPOSE 8000

# Comando para iniciar el servidor de backend. 
# Migraciones se ejecutan al inicio por el framework si es necesario.
CMD ["reflex", "run", "--host", "0.0.0.0", "--port", "8000", "--loglevel", "info"]
