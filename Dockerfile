# Dockerfile

# --- Etapa 1: Construir el Frontend Estático ---
# Usamos una imagen de Node.js para las herramientas de frontend
FROM node:20-slim as frontend-builder

# Instalamos Python y Pip para poder ejecutar el comando de Reflex
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiamos solo los requisitos para instalar dependencias primero
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copiamos todo el código de la aplicación
COPY . .

# Exportamos el frontend. Esto crea la carpeta .web
RUN reflex export --frontend-only --no-zip


# --- Etapa 2: Construir la Imagen Final de Producción ---
# Usamos una imagen ligera de Python
FROM python:3.11-slim

WORKDIR /app

# Instalamos dependencias del sistema operativo y curl (para Caddy)
# "parallel" es para ejecutar backend y caddy al mismo tiempo
RUN apt-get update && apt-get install -y --no-install-recommends parallel curl && rm -rf /var/lib/apt/lists/*

# Copiamos los requisitos de Python y los instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el código de la aplicación
COPY . .

# Copiamos el frontend ya construido desde la etapa anterior
COPY --from=frontend-builder /app/.web ./.web

# Descargamos e instalamos Caddy (servidor web)
RUN curl -L "https://caddyserver.com/api/download?os=linux&arch=amd64" -o /usr/bin/caddy && \
    chmod +x /usr/bin/caddy

# Copiamos los archivos de configuración y el script de inicio
COPY Caddyfile /app/Caddyfile
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Exponemos el puerto 3000 que usará Caddy
EXPOSE 3000

# El script que se ejecutará al iniciar el contenedor
ENTRYPOINT ["/app/entrypoint.sh"]

# El comando por defecto que ejecutará el entrypoint.sh
# Inicia el backend de Reflex y Caddy en paralelo.
CMD ["parallel", "--ungroup", "--halt", "now,fail=1", ":::", "reflex run --backend-only --host 0.0.0.0 --port 8000 --loglevel info", "caddy run --config /app/Caddyfile --adapter caddyfile"]