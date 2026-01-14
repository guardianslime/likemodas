# init_build.py
from sqlmodel import SQLModel, create_engine
# Importamos los modelos de auth para que se registren
from reflex_local_auth.models import LocalUser, LocalAuthSession

print("Iniciando creación de tablas dummy...")

# Usamos la misma DB que pusimos en el rxconfig
engine = create_engine("sqlite:///./reflex_build.db")

# Esto crea las tablas vacías (localuser, etc.)
SQLModel.metadata.create_all(engine)

print("¡Tablas creadas! Ahora puedes hacer el export.")