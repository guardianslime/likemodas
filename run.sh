#!/bin/bash

echo "----> [Paso 1 de 5] Actualizando lista de paquetes del sistema..."
apt-get update

echo "----> [Paso 2 de 5] Instalando dependencias del sistema (ZBar, XCB y X11)..."
# Añadimos libxcb1 para corregir el error técnico y otras librerías gráficas base
apt-get install -y libzbar-dev libxcb1 libx11-6 libxext6 libxrender1

echo "----> [Paso 3 de 5] Verificando si las bibliotecas clave existen..."
# Verificamos ZBar
ls -l /usr/lib/x86_64-linux-gnu/libzbar.so*
# Verificamos XCB
ls -l /usr/lib/x86_64-linux-gnu/libxcb.so*

echo "----> [Paso 4 de 5] Aplicando migraciones a la base de datos..."
alembic upgrade head

echo "----> [Paso 5 de 5] Iniciando el servidor de la aplicación..."
reflex run --backend-only --env prod --backend-host 0.0.0.0 --backend-port $PORT