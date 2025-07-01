# Usa una imagen base de Python 3.12 optimizada.
FROM python:3.12-slim

# Permite a pip instalar paquetes y establece el directorio de trabajo.
ENV PIP_BREAK_SYSTEM_PACKAGES=1
WORKDIR /app

# Instala todas las dependencias de sistema necesarias.
RUN apt-get update && apt-get install -y --no-install-recommends build-essential nodejs npm unzip curl ca-certificates && rm -rf /var/lib/apt/lists/*

# Copia e instala las dependencias de Python.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el código de la aplicación.
COPY . .

# Expone el puerto que usará Reflex (Railway lo mapeará).
EXPOSE 8000

# --- COMANDO DE INICIO DEFINITIVO ---
# 1. 'reflex db init': Prepara la BD para las migraciones.
# 2. 'reflex db migrate': Aplica las migraciones.
# 3. 'uvicorn ...': Inicia el servidor directamente con soporte para proxy (WebSockets).
CMD ["sh", "-c", "reflex db init && reflex db migrate && uvicorn simple_app.simple_app:app --host 0.0.0.0 --port 8000 --proxy-headers"]
