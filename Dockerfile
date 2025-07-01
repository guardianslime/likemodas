# Usa una imagen base de Python 3.11 optimizada.
FROM python:3.12-slim

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

# --- CORRECCIÓN CLAVE ---
# Se actualiza el comando para que coincida con la sintaxis de reflex==0.5.0
# --host -> --backend-host
# --port -> --backend-port
# Se añade --backend-only para asegurar que solo el backend se ejecute en producción.
CMD ["reflex", "run", "--backend-only", "--backend-host", "0.0.0.0", "--backend-port", "8000", "--loglevel", "info"]
