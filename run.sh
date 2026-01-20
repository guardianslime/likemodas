#!/bin/bash

echo "----> [Paso 1 de 5] Actualizando lista de paquetes del sistema..."
apt-get update

echo "----> [Paso 2 de 5] Forzando la instalación de la biblioteca ZBar..."
apt-get install -y libzbar-dev

echo "----> [Paso 3 de 5] Verificando si la biblioteca fue instalada..."
# Este comando nos mostrará si el archivo clave existe.
ls -l /usr/lib/x86_64-linux-gnu/libzbar.so*

echo "----> [Paso 4 de 5] Aplicando migraciones a la base de datos..."
alembic upgrade head

echo "----> [Paso 5 de 5] Iniciando el servidor de la aplicación..."
reflex run --backend-only --env prod --backend-host 0.0.0.0 --backend-port $PORT