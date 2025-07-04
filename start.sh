!/bin/bash

# 1. Instala las dependencias (tu comando original)
pip install -r requirements.txt

# 2. (¡NUEVO!) Aplica las migraciones a la base de datos
# Esto sincronizará tu base de datos en Railway con tus modelos de Python
reflex db migrate

# 3. Inicia el backend de la aplicación (tu comando original)
reflex run --backend-only --env prod