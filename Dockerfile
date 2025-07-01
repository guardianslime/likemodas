# Usa una imagen base de Python 3.12 optimizada.
FROM python:3.12-slim

# Permite a pip instalar paquetes y establece el directorio de trabajo.
ENV PIP_BREAK_SYSTEM_PACKAGES=1
WORKDIR /app

# Instala las dependencias de Python.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el código de la aplicación.
COPY . .

# Expone el puerto que usará Reflex (Railway lo mapeará).
EXPOSE 8000

# Comando para iniciar el servidor de backend en modo producción.
CMD ["reflex", "run", "--env", "prod", "--backend-host", "0.0.0.0", "--backend-port", "8000"]
