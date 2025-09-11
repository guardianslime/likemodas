#!/bin/bash
# Este script se ejecutará cada vez que Railway despliegue tu aplicación.

echo "----> Instalando dependencias..."
pip install -r requirements.txt

echo "----> Aplicando migraciones a la base de datos de producción..."
# --- El comando MODERNO y CORRECTO para aplicar las migraciones ---
# Construye los cimientos (las tablas) en tu base de datos PostgreSQL.
reflex db alembic upgrade head

echo "----> Iniciando el servidor backend..."
# --- El comando MODERNO y CORRECTO para iniciar el servidor ---
# Pone la casa (tu app) sobre los cimientos ya construidos.
reflex run --backend-only --env prod --backend-host 0.0.0.0 --port $PORT