#!/bin/bash
# start.sh (COMANDOS CORREGIDOS)

echo "----> Aplicando migraciones a la base de datos de producción..."
# Corrección 1: Usar el comando directo de alembic.
# Esto funcionará ahora porque el entorno ya está bien configurado.
alembic upgrade head

echo "----> Iniciando el servidor backend..."
# Corrección 2: Usar --backend-port en lugar de --port y quitar el host.
# Railway inyecta el puerto en la variable $PORT y gestiona el host automáticamente.
reflex run --backend-only --env prod --backend-port $PORT