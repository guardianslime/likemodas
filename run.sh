#!/bin/bash

echo "----> Installing dependencies..."
pip install -r requirements.txt

echo "----> Running database migrations..."
# Inicializa la configuración de Alembic (el '|| true' evita errores si ya existe)
reflex db init || true
# Crea un archivo de migración automático (es seguro ejecutarlo incluso si no hay cambios)
reflex db migrate -m "auto-migration from deploy"
# Aplica cualquier migración pendiente a la base de datos
reflex db upgrade

echo "----> Starting backend server..."
# Inicia el servidor del backend para producción, escuchando en todas las interfaces
# y en el puerto que Railway asigne dinámicamente a través de la variable $PORT.
reflex run --backend-only --env prod --host 0.0.0.0 --port $PORT
