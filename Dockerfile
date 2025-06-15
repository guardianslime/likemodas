# Dockerfile
FROM python:3.11-slim-buster

# Instala los paquetes 'unzip' y 'curl' requeridos por Reflex
# apt-get update: Actualiza la lista de paquetes disponibles
# apt-get install -y unzip curl: Instala unzip y curl. '-y' para aceptar automáticamente.
# rm -rf /var/lib/apt/lists/*: Limpia el caché de apt-get para reducir el tamaño de la imagen.
RUN apt-get update && apt-get install -y unzip curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN reflex init

EXPOSE 8000

CMD ["reflex", "run", "--env", "prod", "--port", "8000", "--host", "0.0.0.0"]