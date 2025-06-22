# Dockerfile

# --- Etapa 1: Construir el Frontend Estático ---
# Usamos una imagen de Node.js para las herramientas de frontend
FROM node:20-slim as frontend-builder

# Variable de entorno para permitir a pip instalar paquetes.
ENV PIP_BREAK_SYSTEM_PACKAGES=1

# Instalamos las dependencias del sistema operativo
RUN apt-get update && apt-get install -y python3 python3-pip unzip curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiamos solo los requisitos para instalar dependencias primero
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copiamos todo el código de la aplicación
COPY . .

# ¡SOLUCIÓN DEFINITIVA! Elimina la configuración del sitemap para forzar su desactivación.
RUN rm -f .web/next-sitemap.config.js

# Optimizamos el uso de memoria para el proceso de compilación del frontend.
ENV NODE_OPTIONS="--max-old-space-size=2048"

# Exportamos el frontend.
RUN reflex export --frontend-only --no-zip --loglevel debug


# --- Etapa 2: Construir la Imagen Final de Producción ---
# Usamos una imagen ligera de Python
FROM python:3.11-slim

# Variable de entorno para permitir a pip instalar paquetes.
ENV PIP_BREAK_SYSTEM_PACKAGES=1

WORKDIR /app

# Instalamos dependencias del sistema operativo que necesita tu app y Caddy
RUN apt-get update && apt-get install -y --no-install-recommends git nodejs npm unzip parallel build-essential curl && rm -rf /var/lib/apt/lists/*

# Copiamos los requisitos de Python y los instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el código de la aplicación
COPY . .

# Copiamos el frontend ya construido desde la etapa anterior
COPY --from=frontend-builder /app/.web ./.web

# Descargamos e instalamos Caddy
RUN curl -L "https://caddyserver.com/api/download?os=linux&arch=amd64" -o /usr/bin/caddy && \
    chmod +x /usr/bin/caddy

# Copiamos el Caddyfile
COPY Caddyfile /app/Caddyfile
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Exponemos el puerto 3000 que usará Caddy
EXPOSE 3000

# Establece el entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# El comando para iniciar la aplicación ahora se pasa al entrypoint
CMD ["parallel", "--ungroup", "--halt", "now,fail=1", ":::", "reflex run --backend-only --host 0.0.0.0 --port 8000 --loglevel info", "caddy run --config /app/Caddyfile --adapter caddyfile"]