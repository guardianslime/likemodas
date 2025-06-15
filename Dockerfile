# Dockerfile
FROM python:3.11-slim-buster

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia el archivo de requisitos e instala las dependencias
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copia el resto del código de la aplicación (esto incluye full_stack_python.py, rxconfig.py, etc.)
COPY . .

# Importante: Reflex necesita ejecutar init para configurar los archivos estáticos
# y otros elementos del proyecto en el entorno de build del contenedor.
RUN reflex init

# Expone el puerto por defecto de Reflex (puerto 8000)
EXPOSE 8000

# Comando para ejecutar la aplicación Reflex en producción
CMD ["reflex", "run", "--env", "prod", "--port", "8000", "--host", "0.0.0.0"]