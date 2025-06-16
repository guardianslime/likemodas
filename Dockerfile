# Dockerfile (CAMBIO TEMPORAL SOLO PARA DIAGNÓSTICO)
FROM python:3.11-slim-buster

RUN apt-get update && apt-get install -y unzip curl
RUN pip install gunicorn uvicorn
RUN rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# CAMBIO: Hardcodea el puerto 8000 directamente, en lugar de usar $PORT
# ESTO ES SOLO PARA PROBAR. SI FUNCIONA, EL PROBLEMA ES CÓMO RENDER RESUELVE $PORT.
CMD ["gunicorn", "full_stack_python.full_stack_python:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"] # <-- CAMBIO A 8000
