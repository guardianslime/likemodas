#!/bin/bash

echo "----> Aplicando migraciones a la base de datos..."
alembic upgrade head

echo "----> Iniciando el servidor backend..."
reflex run --backend-only --env prod --backend-host 0.0.0.0 --backend-port $PORT