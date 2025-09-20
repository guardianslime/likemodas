#!/bin/bash
# start.sh (SIMPLIFICADO)

echo "----> Aplicando migraciones a la base de datos de producción..."
# Este comando ahora funcionará porque reflex ya fue instalado por Nixpacks.
reflex db alembic upgrade head

echo "----> Iniciando el servidor backend..."
# Este comando también funcionará.
reflex run --backend-only --env prod --backend-host 0.0.0.0 --port $PORT