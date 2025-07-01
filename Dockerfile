# Usa una imagen base de Python 3.12 optimizada.
FROM python:3.12-slim

ENV PIP_BREAK_SYSTEM_PACKAGES=1
WORKDIR /app

# Instala todas las dependencias de sistema necesarias.
RUN apt-get update && apt-get install -y --no-install-recommends build-essential nodejs npm unzip curl ca-certificates && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# --- COMANDO DE INICIO FINAL ---
# Ejecuta la migración y luego inicia el servidor.
CMD ["sh", "-c", "reflex db migrate && reflex run --env prod --backend-host 0.0.0.0 --backend-port 8000"]
