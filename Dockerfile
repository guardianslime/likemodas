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

Necesito que me digas que necesito para poder subir eso a railway y conectarlo a versel, dime el paso a paso, mira las versiones y todo, quiero conectar y subir la imagen ducke si es posible dime con pasos bien detallados explicando lo que debo hacer y dándome los códigos corregidos para subirlos además de las otras cosas que debería hacer, ten en cuenta que ese código que te estoy pasando ya funciona en Railway pero no logro conectarlo a versel, por favor explica a detalle como lograr la conexión  

# Copia todo el código de la aplicación
COPY . .

# Expone el puerto que usará Reflex
EXPOSE 8000

# Comando para iniciar el servidor de backend. 
# Migraciones se ejecutan al inicio por el framework si es necesario.
CMD ["reflex", "run", "--host", "0.0.0.0", "--port", "8000", "--loglevel", "info"]
