#!/bin/bash
# This script is correct.

echo "----> Instalando dependencias..."
pip install -r requirements.txt

echo "----> Aplicando migraciones a la base de datos de producción..."
# This command correctly runs migrations through the Reflex CLI.
reflex db alembic upgrade head

echo "----> Iniciando el servidor backend..."
# This command starts the app server.
reflex run --backend-only --env prod --backend-host 0.0.0.0 --port $PORT