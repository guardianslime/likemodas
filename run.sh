#!/bin/bash

# Este script se ejecutará cada vez que Railway despliegue tu aplicación.

echo "----> Instalando dependencias..."
pip install -r requirements.txt

echo "----> Aplicando migraciones a la base de datos de producción..."
# Este es el ÚNICO comando de base de datos necesario en producción.
# Aplica los archivos de migración de tu repositorio a la base de datos PostgreSQL de Railway,
# creando las tablas como 'localuser' si no existen.
reflex db upgrade

echo "----> Iniciando el servidor backend..."
# Inicia la aplicación en el puerto que Railway asigne dinámicamente.
reflex run --backend-only --env prod --host 0.0.0.0 --port $PORT