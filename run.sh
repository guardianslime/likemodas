#!/bin/bash

# Este script se ejecutará cada vez que Railway despliegue tu aplicación.

echo "----> Instalando dependencias..."
pip install -r requirements.txt

echo "----> Aplicando migraciones a la base de datos de producción..."
# --- COMANDO CORREGIDO ---
# En versiones recientes de Reflex, 'upgrade' se hace a través de alembic.
# 'head' significa "actualizar a la última versión disponible".
reflex db alembic upgrade head

echo "----> Iniciando el servidor backend..."
# --- COMANDO CORREGIDO ---
# La opción '--host' fue renombrada a '--backend-host'.
# Inicia la aplicación en el puerto que Railway asigne dinámicamente.
reflex run --backend-only --env prod --backend-host 0.0.0.0 --port $PORT

