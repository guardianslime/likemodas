#!/bin/bash
# entrypoint.sh

# Detener el script si algún comando falla
set -e

# Aplicar migraciones de la base de datos
echo "--> Applying database migrations..."
alembic upgrade head

# Iniciar la aplicación principal (el CMD original del Dockerfile)
echo "--> Starting application..."
exec "$@"