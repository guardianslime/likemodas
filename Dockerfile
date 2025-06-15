# Dockerfile
FROM python:3.11-slim-buster

# Instala los paquetes 'unzip' y 'curl' requeridos por Reflex
RUN apt-get update && apt-get install -y unzip curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN reflex init

EXPOSE 8000

# ¡IMPORTANTE! Cambiado --port a --backend-port
CMD ["reflex", "run", "--env", "prod", "--backend-host", "0.0.0.0", "--backend-port", "8000"]